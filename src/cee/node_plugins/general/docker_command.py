import subprocess
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field
from cee.node_plugins.base import Base


class DockerCommand(Base):
    """Execute a Docker CLI command."""

    class InputSpec(BaseModel):
        """Docker command node input spec."""

        pass

    class OutputSpec(BaseModel):
        """Docker command node output spec."""

        pass

    class ParamSpec(BaseModel):
        """Docker command node parameter spec."""

        command: list[str] = Field(
            ...,
            min_length=2,
            description=(
                "Docker command represented as a list of strings. "
                "The first element must be 'docker'."
            ),
        )
        timeout_seconds: float | None = Field(
            default=None,
            gt=0,
            description="Optional command timeout in seconds.",
        )

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def _normalize_volume_paths(
        self,
        command: list[str],
    ) -> list[str]:
        """
        Convert relative Docker bind-mount source paths into absolute paths.

        Example:
            vision/model:/data/model:ro

        becomes:
            /absolute/project/path/vision/model:/data/model:ro
        """
        normalized_command = command.copy()

        index = 0

        while index < len(normalized_command):
            argument = normalized_command[index]

            # Support:
            #   -v host_path:container_path
            #   --volume host_path:container_path
            if argument in {"-v", "--volume"}:
                if index + 1 >= len(normalized_command):
                    raise ValueError(
                        f"[Node {self.node_id}] Missing volume specification "
                        f"after {argument!r}."
                    )

                normalized_command[index + 1] = (
                    self._normalize_volume_specification(
                        normalized_command[index + 1]
                    )
                )

                index += 2
                continue

            # Support:
            #   --volume=host_path:container_path
            if argument.startswith("--volume="):
                volume_specification = argument.removeprefix("--volume=")

                normalized_command[index] = (
                    "--volume="
                    + self._normalize_volume_specification(
                        volume_specification
                    )
                )

            index += 1

        return normalized_command

    def _normalize_volume_specification(
        self,
        volume_specification: str,
    ) -> str:
        """
        Normalize the source part of a Docker volume specification.

        Supported forms:
            host_path:container_path
            host_path:container_path:ro
            host_path:container_path:rw
        """
        parts = volume_specification.split(":", maxsplit=2)

        if len(parts) < 2:
            raise ValueError(
                f"[Node {self.node_id}] Invalid Docker volume specification: "
                f"{volume_specification!r}"
            )

        source = parts[0]
        target = parts[1]
        mode = parts[2] if len(parts) == 3 else None

        if not source:
            raise ValueError(
                f"[Node {self.node_id}] Docker volume source must not be empty."
            )

        if not target:
            raise ValueError(
                f"[Node {self.node_id}] Docker volume target must not be empty."
            )

        # A source beginning with "/" is already an absolute Linux path.
        #
        # Relative paths such as:
        #   vision/model
        #   ./vision/model
        #
        # are resolved relative to the workflow engine's current
        # working directory.
        if not Path(source).is_absolute():
            source = str(Path(source).resolve())

        if mode:
            return f"{source}:{target}:{mode}"

        return f"{source}:{target}"

    def run(
        self,
        input_data: dict | None = None,
    ) -> None:
        """Execute the configured Docker command."""
        print(f"[Node {self.node_id}] Execution started")

        # This node currently has no required input.
        self.InputSpec.model_validate(input_data or {})

        # Validate node parameters.
        validated_params = self.ParamSpec.model_validate(self.params)

        command = validated_params.command
        timeout_seconds = validated_params.timeout_seconds

        # Prevent this generic node from executing arbitrary non-Docker commands.
        if command[0] != "docker":
            raise ValueError(
                f"[Node {self.node_id}] Only Docker commands are allowed. "
                f"Received executable: {command[0]!r}"
            )

        # Convert relative bind-mount paths into absolute host paths.
        command = self._normalize_volume_paths(command)

        print(
            f"[Node {self.node_id}] Executing command: "
            f"{subprocess.list2cmdline(command)}"
        )

        process: subprocess.Popen[str] | None = None

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            assert process.stdout is not None

            # Print container output line by line.
            for line in process.stdout:
                print(
                    f"[Node {self.node_id}] {line.rstrip()}",
                    flush=True,
                )

            return_code = process.wait(timeout=timeout_seconds)

            if return_code != 0:
                raise subprocess.CalledProcessError(
                    returncode=return_code,
                    cmd=command,
                )

        except subprocess.TimeoutExpired as error:
            if process is not None:
                process.kill()
                process.wait()

            raise TimeoutError(
                f"[Node {self.node_id}] Docker command exceeded "
                f"the timeout of {timeout_seconds} seconds."
            ) from error

        except FileNotFoundError as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Docker CLI was not found. "
                "Ensure Docker is installed and available in PATH."
            ) from error

        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Docker command failed "
                f"with exit code {error.returncode}."
            ) from error

        print(f"[Node {self.node_id}] Execution completed")
