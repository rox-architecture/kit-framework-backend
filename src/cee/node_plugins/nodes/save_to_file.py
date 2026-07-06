from typing import Any
from pydantic import BaseModel
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base


class SaveToFile(Base):
    """Save to file node."""

    # Predefined Output specification
    class InputSpec(BaseModel):
        """Safe to file node input spec."""

        data: Item

    class ParamSpec(BaseModel):
        """Safe to file node param spec."""

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None:
        print("SaveToFile object triggered")
