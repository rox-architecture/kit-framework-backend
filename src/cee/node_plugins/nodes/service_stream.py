from typing import Any
from pydantic import BaseModel
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base


class ServiceStream(Base):
    """Service stream node."""

    # Predefined Input specification
    class InputSpec(BaseModel):
        """Service stream node input spec."""

    # Predefined Output specification
    class OutputSpec(BaseModel):
        """Service stream node output spec."""
        output_0: Item

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, config: dict, input_data: dict | None = None) -> None:
        """Run the node."""
        print("ServiceStream object triggered")
