from typing import Any, Literal

from pydantic import Field

from cee.models.edc.entity import JsonLdEntityNoId


class NegotiationInitiation(JsonLdEntityNoId):
    """EDC negotiation initiation model."""

    at_type: Literal["NegotiationRequest"] = Field("NegotiationRequest", alias="@type")
    counter_party_address: str
    protocol: str
    policy: Any
    callback_addresses: Any = None
