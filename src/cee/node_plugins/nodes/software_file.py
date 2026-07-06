from typing import Any
from pydantic import BaseModel
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base


class SoftwareFile(Base):
    """Software file node."""

    # Predefined Output specification
    class OutputSpec(BaseModel):
        """Software file node output spec."""

        data: Item

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        """Run the node."""
        print("SoftwareFile object triggered")
