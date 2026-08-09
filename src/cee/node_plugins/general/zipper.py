from pydantic import BaseModel
from pathlib import Path
from cee.node_plugins.base import Base
import shutil
from typing import Any
import tempfile
import os

class Zipper(Base):
    """Zipper node."""
    
    # Input is always a list of Items
    class InputSpec(BaseModel):
        pass

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        pass

    class ParamSpec(BaseModel):
        """Zipper node param spec."""
        target_directory: Path
        output_path: Path

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        print(f"[Node {self.node_id}] Execution started", flush=True)

        artifact_root = Path(
            os.environ.get("ARTIFACT_ROOT", "/artifacts")
        ).resolve()

        requested_target = Path(self.params["target_directory"])
        requested_output = Path(self.params["output_path"])

        if requested_target.is_absolute():
            raise ValueError(
                "target_directory must be relative to ARTIFACT_ROOT"
            )

        if requested_output.is_absolute():
            raise ValueError(
                "output_path must be relative to ARTIFACT_ROOT"
            )

        target_directory = (artifact_root / requested_target).resolve()
        output_path = (artifact_root / requested_output).resolve()

        if not target_directory.is_relative_to(artifact_root):
            raise ValueError(
                "target_directory must remain inside ARTIFACT_ROOT"
            )

        if not output_path.is_relative_to(artifact_root):
            raise ValueError(
                "output_path must remain inside ARTIFACT_ROOT"
            )

        if not target_directory.is_dir():
            raise NotADirectoryError(
                f"{target_directory} is not a directory"
            )

        if output_path.suffix.lower() != ".zip":
            output_path = output_path.with_suffix(".zip")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            temporary_base = Path(tmpdir) / "archive"

            temporary_archive = Path(
                shutil.make_archive(
                    base_name=str(temporary_base),
                    format="zip",
                    root_dir=str(target_directory),
                )
            )

            shutil.move(temporary_archive, output_path)

        print(
            f"[Node {self.node_id}] Created archive: {output_path}",
            flush=True,
        )
        self.finished = True