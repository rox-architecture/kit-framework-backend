from pydantic import BaseModel, Field
from typing import Any

class Item(BaseModel):
    json_data: dict[str, Any] = Field(default_factory=dict)
    binary: bytes
