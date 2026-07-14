from pydantic import Field

from cee.models.edc.entity import JsonLdEntityNoId


class EdrDataAddress(JsonLdEntityNoId):
    """EDC EDR data address model."""

    type: str
    authorization: str
    endpoint: str
    endpoint_type: str
    flow_type: str
    transfer_type_destination: str
    audience: str = Field(..., alias="https://w3id.org/tractusx/auth/audience")
    expires_in: str = Field(..., alias="https://w3id.org/tractusx/auth/expiresIn")
    refresh_audience: str = Field(
        ..., alias="https://w3id.org/tractusx/auth/refreshAudience"
    )
    refresh_endpoint: str = Field(
        ..., alias="https://w3id.org/tractusx/auth/refreshEndpoint"
    )
    refresh_token: str = Field(..., alias="https://w3id.org/tractusx/auth/refreshToken")
