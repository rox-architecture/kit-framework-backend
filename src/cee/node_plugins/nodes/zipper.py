from pydantic import BaseModel
from pathlib import Path
from cee.node_plugins.base import Base
import shutil
import tempfile

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

    def run(self, config: dict, input_data: dict | None = None) -> None:
        print(f"[Node {self.node_id}] Execution started")
        
        # read parameters
        target_directory = Path(self.params["target_directory"])
        output_path = Path(self.params["output_path"])

        if not target_directory.is_dir():
            raise NotADirectoryError(
                f"{target_directory} is not a directory."
            )
        
        if output_path.suffix != ".zip":
            output_path = output_path.with_suffix(".zip")

        # create parent directories
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

            shutil.move(
                str(temporary_archive),
                str(output_path),
            )

        print(f"[Node {self.node_id}] Created archive: {output_path}")
        self.finished = True