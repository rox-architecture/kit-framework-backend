from typing import Any
from pydantic import BaseModel
from cee.schema.execution_schema import Item
from pathlib import Path
from cee.node_plugins.base import Base
import os

class SaveToFile(Base):
    """Save to file node."""

    class InputSpec(BaseModel):
        """Safe to file node input spec."""
        input_0: Item

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        pass

    class ParamSpec(BaseModel):
        """Safe to file node param spec."""
        file_path: Path

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        print(f"[Node {self.node_id}] Execution started")

        validated_input = self.InputSpec.model_validate(input_data)
        binary = validated_input.input_0.binary

        artifact_root = Path(
            os.environ.get("ARTIFACT_ROOT", "/artifacts")
        ).resolve()

        requested_path = Path(self.params["file_path"])

        if requested_path.is_absolute():
            raise ValueError("file_path must be relative to ARTIFACT_ROOT")

        file_path = (artifact_root / requested_path).resolve()

        if not file_path.is_relative_to(artifact_root):
            raise ValueError("file_path must remain inside ARTIFACT_ROOT")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(binary)

        print(f"[Node {self.node_id}] Saved file to {file_path}", flush=True)
