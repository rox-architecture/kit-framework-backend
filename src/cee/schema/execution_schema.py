from pydantic import BaseModel, Field
from typing import Any


class Item(BaseModel):
    """Item model."""

    json_data: dict[str, Any] = Field(default_factory=dict)
    binary: bytes
