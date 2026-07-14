from pydantic import BaseModel
from pathlib import Path
from cee.node_plugins.base import Base
import shutil

class Unzipper(Base):
    """Unzipper node."""

    class ParamSpec(BaseModel):
        """Unzipper node param spec."""
        target_zip: Path
        extract_directory: Path

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        print(f"[Node {self.node_id}] Execution started")

        """Run the node."""
        print(f"[Node {self.node_id}] Execution started")

        # Read parameters
        target_zip = Path(self.params["target_zip"])
        extract_path = Path(self.params["extract_directory"])

        # Check input archive
        if not target_zip.is_file():
            raise FileNotFoundError(
                f"Archive not found: {target_zip}"
            )

        if target_zip.suffix != ".zip":
            raise ValueError(
                f"Expected a .zip archive: {target_zip}"
            )

        # Create extraction directory if necessary
        extract_path.mkdir(parents=True, exist_ok=True)

        # Extract archive
        shutil.unpack_archive(
            filename=str(target_zip),
            extract_dir=str(extract_path),
            format="zip",
        ) 

        self.finished = True