from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

Context = str | dict[str, Any] | list[Any]


class Entity(BaseModel):
    """Base EDC entity model."""

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True
    )


class JsonLdEntityNoId(Entity):
    """Base JSON-LD EDC entity model (without @id)."""

    at_context: Context = Field(default_factory=dict, alias="@context")
    at_type: str | list[str] | None = Field(None, alias="@type")


class JsonLdEntity(Entity):
    """Base JSON-LD EDC entity model."""

    at_context: Context = Field(default_factory=dict, alias="@context")
    at_id: str = Field(..., alias="@id")
    at_type: str | list[str] | None = Field(None, alias="@type")
