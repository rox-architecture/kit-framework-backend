from typing import Any
from pydantic import BaseModel
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base


class ServiceFile(Base):
    """Service file node."""

    # Predefined Input specification
    class InputSpec(BaseModel):
        """Service file node input spec."""

    # Predefined Output specification
    class OutputSpec(BaseModel):
        """Service file node output spec."""

        data: Item

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        """Run the node."""
        print("ServiceFile object triggered")
