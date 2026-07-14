from pydantic import BaseModel
from cee.schema.execution_schema import Item
from pathlib import Path
from cee.node_plugins.base import Base
import shutil

class Zipper(Base):
    """Save to file node."""

    class ParamSpec(BaseModel):
        """Safe to file node param spec."""
        target_directory: Path
        output_path: Path

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        print(f"[Node {self.node_id}] Execution started")
        
        # read parameters
        target_directory = Path(self.params["target_directory"])
        output_path = self.params["output_path"]

        if not target_directory.is_dir():
            raise NotADirectoryError(
                f"{target_directory} is not a directory."
            )
        
        if output_path.suffix != ".zip":
            output_path = output_path.with_suffix(".zip")

        # create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.make_archive(
            base_name=str(output_path.with_suffix("")),
            format="zip",
            root_dir=str(target_directory),
        )

        self.finished = True