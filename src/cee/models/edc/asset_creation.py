from typing import Any, Literal

from pydantic import Field

from cee.models.edc.data_address import DataAddress
from cee.models.edc.entity import JsonLdEntity


class AssetCreation(JsonLdEntity):
    """EDC asset creation model."""

    at_type: Literal["Asset"] = Field("Asset", alias="@type")
    properties: dict[str, Any]
    private_properties: dict[str, Any] | None = None
    data_address: DataAddress
