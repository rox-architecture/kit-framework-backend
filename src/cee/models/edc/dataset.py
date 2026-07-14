from typing import Any, ClassVar, cast

from pydantic import Field, field_validator, model_serializer, model_validator

from cee.models.edc.entity import JsonLdEntity


class Dataset(JsonLdEntity):
    """EDC dataset model."""

    DEFAULT_KEYS: ClassVar[set[str]] = {
        "@context",
        "@id",
        "@type",
        "odrl:hasPolicy",
        "dcat:distribution",
    }

    policies: list[Any] = Field(..., alias="odrl:hasPolicy")
    distribution: list[Any] = Field(..., alias="dcat:distribution")
    properties: dict[str, Any]

    @field_validator("policies", "distribution", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list[Any]:
        """Wrap the given element into a list if it is not one already."""
        if isinstance(v, list):
            return v
        return [v]

    @model_validator(mode="before")
    @classmethod
    def gather_properties(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Gather non standard values in properties."""
        default = {k: v for k, v in values.items() if k in cls.DEFAULT_KEYS}
        properties = {k: v for k, v in values.items() if k not in cls.DEFAULT_KEYS}
        return {**default, "properties": properties}

    @model_serializer(mode="plain")
    def model_serialize(self) -> dict[Any, Any]:
        """Serialize the model."""
        out = {}

        for name, field in type(self).model_fields.items():
            alias = field.alias or name
            value = getattr(self, name)

            if name == "properties" and isinstance(value, dict):
                out.update(value)
            else:
                out[alias] = value

        out.pop("@context", None)
        return out

    @property
    def asset_id(self) -> str:
        """Get the asset ID."""
        return cast("str", self.get_property("id"))

    def get_property(self, key: str) -> Any:
        """Get the property with the given key."""
        return self.properties.get(key)
