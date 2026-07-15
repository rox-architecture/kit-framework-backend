from typing import Any, Literal
from pydantic import BaseModel, HttpUrl, field_validator
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY
import docker
import tempfile
from pathlib import Path
import io
import os
import tarfile
import zipfile


class ContainerImage(Base):
    """Data container node."""

    class ParamSpec(BaseModel):
        """Data file node param spec."""
        adapter_type: str
        provider_bpn: str
        provider_url: HttpUrl
        asset_id: str

        representation: Literal['dockerfile', 'archive'] # TODO: add more types like [oci-archive, oci-registry]
        platforms: set[ Literal['linux/amd64', 'linux/arm64', 'windows/amd64', 'windows/arm64'] ]

        image_name: str
        image_tag: str
        registry_addr: str | None = None

        # avoid case sensitivity
        @field_validator("platforms", mode="before")
        @classmethod
        def normalize_platforms(cls, v):
            if isinstance(v, str):
                return {v}
            return v

        # avoid case sensitivity (e.g., Dockerfile == dockerfile)       
        @field_validator("representation", mode="before")
        @classmethod
        def normalize(cls, v):
            if isinstance(v, str):
                return v.lower()
            return v
        
    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

        # select the correct adapter based on the parameter value
        adapter_type = self.params["adapter_type"]
        self.adapter = ADAPTER_REGISTRY[adapter_type]()

    def run(self, input_data: dict | None = None) -> None:
        """Run the node."""
        print(f"[Node {self.node_id}] Execution started")

        representation = self.params['representation']

        # read parameter values
        provider_bpn = self.params['provider_bpn']
        provider_url = self.params['provider_url']
        asset_id = self.params['asset_id']
        image_name = self.params['image_name']
        image_tag = self.params['image_tag']
        registry = self.params.get("registry_addr")

        # registry parameter maybe None
        if registry:
            registry = registry.rstrip("/")
            full_image_name = f"{registry}/{image_name}:{image_tag}"
            push = True
        else:
            full_image_name = f"{image_name}:{image_tag}"
            push = False

        # access the dataspace asset
        try:
            response = self.adapter.transfer_data_pull(asset_id)
        except Exception as e:
            # the error caused by non-negotiated node, we negotiate automatically here for now
            print("negotiation triggered")
            ack = self.adapter.initiate_negotiation(provider_bpn, provider_url, asset_id)
            response = self.adapter.transfer_data_pull(asset_id)

        # instantiate the docker object
        client = docker.from_env()
        
        # ----------------------------------------------------
        # Handling different cases of accessing container images
        # ----------------------------------------------------
        with tempfile.TemporaryDirectory() as tmpdir: # create a temporary directory to work on
            context = Path(tmpdir)

            match representation:

                case "dockerfile":
                    dockerfile_content = response.text
                    dockerfile = context / "Dockerfile"
                    dockerfile.write_text(dockerfile_content, encoding="utf-8")
                                    
                case "archive":
                    archive_bytes = response.content
                    archive_path = context / "archive"
                    archive_path.write_bytes(archive_bytes) 

                    
                    if zipfile.is_zipfile(archive_path):
                        with zipfile.ZipFile(archive_path) as zf:
                            zf.extractall(context)

                    elif tarfile.is_tarfile(archive_path):
                        with tarfile.open(archive_path) as tf:
                            tf.extractall(context)

                    else:
                        raise ValueError("Unsupported archive format.")

                    archive_path.unlink()
                    dockerfile = next(context.rglob("Dockerfile"))
                    context = dockerfile.parent

                case _: # for invalid representation values
                    raise ValueError(f"Unsupported representation: {representation}")
    
            # ----------------------------------------------------
            # Build image
            # ----------------------------------------------------
            # check that dockerfile exists
            if not dockerfile.is_file():
                raise FileNotFoundError(
                    "Dockerfile not found at its root."
                )
            
            print(f"[Node {self.node_id}] Building the container image")

            image, build_logs = client.images.build(
                path=str(context),
                dockerfile="Dockerfile",
                tag=full_image_name,
                rm=True,
            )

            for log in build_logs:
                if "stream" in log:
                    for line in log["stream"].splitlines():
                        if line:
                            print(f"[Node {self.node_id}] {line}")

        # ----------------------------------------------------
        # Push image
        # ----------------------------------------------------
        if push:
            print(f"[Node {self.node_id}] Pushing the container image {full_image_name}...")

            push_logs = client.images.push(
                repository=f"{registry}/{image_name}",
                tag=image_tag,
                stream=True,
                decode=True,
            )

            for log in push_logs:
                if "status" in log:
                    message = log["status"]
                    if "progress" in log:
                        message += f" {log['progress']}"
                    print(f"[Node {self.node_id}] {message}")

                elif "aux" in log:
                    print(f"[Node {self.node_id}] {log['aux']}")

                elif "error" in log:
                    print(f"[Node {self.node_id}] ERROR: {log['error']}")

                else:
                    print(f"[Node {self.node_id}] {log}")

        self.finished = True