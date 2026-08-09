"""Container image node implementation."""

from __future__ import annotations

import os
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Literal

import docker
from pydantic import BaseModel, Field, HttpUrl, field_validator

from cee.node_plugins.dlr_dataspace.dlr_adapter import DlrAdapter

from cee.node_plugins.base import Base

Platform = Literal[
    "linux/amd64",
    "linux/arm64",
    "windows/amd64",
    "windows/arm64",
]

class ContainerImage(Base):
    """Pull a Dockerfile or source archive, then build and optionally push it."""

    class InputSpec(BaseModel):
        """Container image node input spec."""

        pass

    class OutputSpec(BaseModel):
        """Container image node output spec."""

        pass

    class ParamSpec(BaseModel):
        """Container image node parameter spec."""

        provider_bpn: str
        provider_url: HttpUrl
        asset_id: str

        representation: Literal["dockerfile", "archive"]
        platforms: set[Platform] = Field(min_length=1)

        image_name: str
        image_tag: str
        registry_addr: str | None = None

        @field_validator("platforms", mode="before")
        @classmethod
        def normalize_platforms(cls, value: Any) -> Any:
            """Allow one platform to be supplied as a string."""
            if isinstance(value, str):
                return {value.lower()}
            if isinstance(value, (list, set, tuple)):
                return {
                    item.lower() if isinstance(item, str) else item
                    for item in value
                }
            return value

        @field_validator("representation", mode="before")
        @classmethod
        def normalize_representation(cls, value: Any) -> Any:
            """Normalize representation names case-insensitively."""
            if isinstance(value, str):
                return value.lower()
            return value

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the node and its selected data-transfer adapter."""
        super().__init__(node)

        validated_params = self.ParamSpec.model_validate(self.params)
        self.adapter = DlrAdapter()

    @staticmethod
    def _safe_extract_zip(archive_path: Path, destination: Path) -> None:
        """Extract a ZIP without allowing members to escape the destination."""
        destination = destination.resolve()

        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                member_path = (destination / member.filename).resolve()
                if not member_path.is_relative_to(destination):
                    raise ValueError(
                        f"Unsafe path in ZIP archive: {member.filename!r}"
                    )

            archive.extractall(destination)

    @staticmethod
    def _safe_extract_tar(archive_path: Path, destination: Path) -> None:
        """Extract a TAR using Python's restrictive data-member filter."""
        with tarfile.open(archive_path) as archive:
            archive.extractall(destination, filter="data")

    @staticmethod
    def _find_dockerfile(context: Path) -> Path:
        """Find exactly one Dockerfile in an extracted build context."""
        dockerfiles = [path for path in context.rglob("Dockerfile") if path.is_file()]

        if not dockerfiles:
            raise FileNotFoundError("Dockerfile not found in the downloaded archive.")

        if len(dockerfiles) > 1:
            locations = ", ".join(str(path.relative_to(context)) for path in dockerfiles)
            raise ValueError(f"Multiple Dockerfiles found in archive: {locations}")

        return dockerfiles[0]

    @staticmethod
    def _get_native_platform(client: docker.DockerClient) -> str:
        """Return the Docker daemon platform in canonical OS/architecture form."""
        daemon_info = client.info()
        operating_system = str(daemon_info["OSType"]).lower()
        architecture = str(daemon_info["Architecture"]).lower()

        architecture_mapping = {
            "x86_64": "amd64",
            "amd64": "amd64",
            "aarch64": "arm64",
            "arm64": "arm64",
            "armv8": "arm64",
        }
        architecture = architecture_mapping.get(architecture, architecture)

        return f"{operating_system}/{architecture}"

    def run(self, input_data: dict | None = None) -> None:
        """Download, build, and optionally push the configured container image."""
        print(f"[Node {self.node_id}] Execution started", flush=True)

        self.InputSpec.model_validate(input_data or {})
        params = self.ParamSpec.model_validate(self.params)

        registry = params.registry_addr.rstrip("/") if params.registry_addr else None
        full_image_name = (
            f"{registry}/{params.image_name}:{params.image_tag}"
            if registry
            else f"{params.image_name}:{params.image_tag}"
        )

        response = self.adapter.transfer_data_pull(params.asset_id)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()

        artifact_root = Path(
            os.environ.get("ARTIFACT_ROOT", "/artifacts")
        ).resolve()
        artifact_root.mkdir(parents=True, exist_ok=True)

        client = docker.from_env()

        try:
            client.ping()

            native_platform = self._get_native_platform(client)
            if native_platform not in params.platforms:
                raise RuntimeError(
                    f"[Node {self.node_id}] The asset does not support the "
                    f"Docker daemon platform {native_platform!r}. Supported "
                    f"platforms: {sorted(params.platforms)}"
                )

            print(
                f"[Node {self.node_id}] Native platform {native_platform} is supported",
                flush=True,
            )

            # The temporary build context lives on the shared artifact volume and
            # is removed automatically after the build, including after failures.
            with tempfile.TemporaryDirectory(
                dir=artifact_root,
                prefix=f"container-build-{self.node_id}-",
            ) as temporary_directory:
                context = Path(temporary_directory)

                if params.representation == "dockerfile":
                    dockerfile = context / "Dockerfile"
                    dockerfile.write_text(response.text, encoding="utf-8")

                elif params.representation == "archive":
                    archive_path = context / "downloaded-archive"
                    archive_path.write_bytes(response.content)

                    if zipfile.is_zipfile(archive_path):
                        self._safe_extract_zip(archive_path, context)
                    elif tarfile.is_tarfile(archive_path):
                        self._safe_extract_tar(archive_path, context)
                    else:
                        raise ValueError("Unsupported archive format; expected ZIP or TAR.")

                    archive_path.unlink()
                    dockerfile = self._find_dockerfile(context)
                    context = dockerfile.parent

                else:
                    raise ValueError(
                        f"Unsupported representation: {params.representation!r}"
                    )

                if not dockerfile.is_file():
                    raise FileNotFoundError("Dockerfile not found in the build context.")

                print(
                    f"[Node {self.node_id}] Building image {full_image_name}",
                    flush=True,
                )

                _, build_logs = client.images.build(
                    path=str(context),
                    dockerfile="Dockerfile",
                    tag=full_image_name,
                    rm=True,
                )

                for log in build_logs:
                    if "stream" in log:
                        for line in log["stream"].splitlines():
                            if line:
                                print(f"[Node {self.node_id}] {line}", flush=True)
                    elif "error" in log:
                        raise RuntimeError(log["error"])

            if registry:
                print(
                    f"[Node {self.node_id}] Pushing image {full_image_name}",
                    flush=True,
                )

                push_logs = client.images.push(
                    repository=f"{registry}/{params.image_name}",
                    tag=params.image_tag,
                    stream=True,
                    decode=True,
                )

                for log in push_logs:
                    if "error" in log:
                        raise RuntimeError(log["error"])

                    if "status" in log:
                        message = log["status"]
                        if "progress" in log:
                            message += f" {log['progress']}"
                        print(f"[Node {self.node_id}] {message}", flush=True)
                    elif "aux" in log:
                        print(f"[Node {self.node_id}] {log['aux']}", flush=True)

            self.finished = True
            print(f"[Node {self.node_id}] Execution completed", flush=True)

        except docker.errors.DockerException as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Docker operation failed: {error}"
            ) from error
        finally:
            client.close()
