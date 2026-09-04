import subprocess
from typing import Any

from pydantic import BaseModel, Field

from cee.node_plugins.base import Base


class BashCommand(Base):
    """Execute a Bash command."""

    class InputSpec(BaseModel):
        """Bash command node input spec."""

        pass

    class OutputSpec(BaseModel):
        """Bash command node output spec."""

        pass

    class ParamSpec(BaseModel):
        """Bash command node parameter spec."""

        command: str = Field(
            ...,
            min_length=1,
            description="Bash command to execute.",
        )

        timeout_seconds: float | None = Field(
            default=None,
            gt=0,
            description="Optional command timeout in seconds.",
        )

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(
        self,
        input_data: dict | None = None,
    ) -> None:
        """Execute the configured Bash command."""
        print(f"[Node {self.node_id}] Execution started")

        self.InputSpec.model_validate(input_data or {})

        validated_params = self.ParamSpec.model_validate(self.params)

        command = validated_params.command
        timeout_seconds = validated_params.timeout_seconds

        print(
            f"[Node {self.node_id}] Executing command: {command}",
            flush=True,
        )

        process: subprocess.Popen[str] | None = None

        try:
            process = subprocess.Popen(
                ["bash", "-lc", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            assert process.stdout is not None

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
                f"[Node {self.node_id}] Bash command exceeded "
                f"the timeout of {timeout_seconds} seconds."
            ) from error

        except FileNotFoundError as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Bash was not found. "
                "Ensure Bash is installed and available in PATH."
            ) from error

        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Bash command failed "
                f"with exit code {error.returncode}."
            ) from error

        print(f"[Node {self.node_id}] Execution completed")