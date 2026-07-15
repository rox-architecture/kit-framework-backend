from typing import Any

from pydantic import Field, field_validator

from cee.models.edc.dataset import Dataset
from cee.models.edc.entity import JsonLdEntity


class Catalog(JsonLdEntity):
    """EDC catalog model."""

    datasets: list[Dataset] = Field(default_factory=list, alias="dcat:dataset")
    catalogs: list[Any] = Field(default_factory=list, alias="dcat:catalog")
    distributions: list[Any] = Field(default_factory=list, alias="dcat:distribution")
    services: list[Any] = Field(default_factory=list, alias="dcat:service")
    participant_id: str = Field(..., alias="dspace:participantId")
    # counter_party_address: str
    # originator: str

    @field_validator("datasets", "catalogs", "distributions", "services", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list[Any]:
        """Wrap the given element into a list if it is not one already."""
        if isinstance(v, list):
            return v
        return [v]
