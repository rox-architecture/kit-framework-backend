from pydantic import BaseModel
from pathlib import Path
from typing import Any
from cee.node_plugins.base import Base
import shutil
import os

class Unzipper(Base):
    """Unzipper node."""
    
    # Input is always a list of Items
    class InputSpec(BaseModel):
        pass

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        pass

    class ParamSpec(BaseModel):
        """Unzipper node param spec."""
        target_zip: Path
        extract_directory: Path

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        """Extract a ZIP archive inside ARTIFACT_ROOT."""
        print(f"[Node {self.node_id}] Execution started", flush=True)

        artifact_root = Path(
            os.environ.get("ARTIFACT_ROOT", "/artifacts")
        ).resolve()

        requested_zip = Path(self.params["target_zip"])
        requested_extract_path = Path(
            self.params["extract_directory"]
        )

        # Require paths relative to ARTIFACT_ROOT
        if requested_zip.is_absolute():
            raise ValueError(
                "target_zip must be relative to ARTIFACT_ROOT"
            )

        if requested_extract_path.is_absolute():
            raise ValueError(
                "extract_directory must be relative to ARTIFACT_ROOT"
            )

        target_zip = (artifact_root / requested_zip).resolve()
        extract_path = (
            artifact_root / requested_extract_path
        ).resolve()

        # Prevent paths such as ../../outside
        if not target_zip.is_relative_to(artifact_root):
            raise ValueError(
                "target_zip must remain inside ARTIFACT_ROOT"
            )

        if not extract_path.is_relative_to(artifact_root):
            raise ValueError(
                "extract_directory must remain inside ARTIFACT_ROOT"
            )

        if not target_zip.is_file():
            raise FileNotFoundError(
                f"Archive not found: {target_zip}"
            )

        if target_zip.suffix.lower() != ".zip":
            raise ValueError(
                f"Expected a .zip archive: {target_zip}"
            )

        extract_path.mkdir(parents=True, exist_ok=True)

        shutil.unpack_archive(
            filename=target_zip,
            extract_dir=extract_path,
            format="zip",
        )

        print(
            f"[Node {self.node_id}] Extracted archive to: "
            f"{extract_path}",
            flush=True,
        )

        self.finished = True