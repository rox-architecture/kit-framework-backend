from typing import Any
from pydantic import BaseModel
from cee.schema.execution_schema import Item
from pathlib import Path
from cee.node_plugins.base import Base


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

    def run(self, config: dict, input_data: dict | None = None) -> None:
        print(f"[Node {self.node_id}] Execution started")
        # check input schema
        validated_input = self.InputSpec.model_validate(input_data)

        # obtain the binary raw data to save into a file
        binary = validated_input.input_0.binary

        # get the target file path including the file name
        file_path = self.params['file_path']
        
        # create directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # write to a file
        with open(file_path, 'wb') as f:
            f.write(binary)
