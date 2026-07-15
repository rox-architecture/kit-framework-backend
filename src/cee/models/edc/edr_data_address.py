from pydantic import AliasChoices, Field

from cee.models.edc.entity import JsonLdEntityNoId


class EdrDataAddress(JsonLdEntityNoId):
    """EDC EDR data address model."""

    type: str
    authorization: str
    endpoint: str
    endpoint_type: str
    flow_type: str | None = None # None is required for T-System dataspace adapter
    transfer_type_destination: str | None = None # None is required for T-System dataspace adapter

    audience: str = Field(
        validation_alias=AliasChoices(
            "tx-auth:audience", # for T-System dataspace
            "https://w3id.org/tractusx/auth/audience",
        )
    )

    expires_in: str = Field(
        validation_alias=AliasChoices(
            "tx-auth:expiresIn", # for T-System dataspace
            "https://w3id.org/tractusx/auth/expiresIn",
        )
    )

    refresh_audience: str = Field(
        validation_alias=AliasChoices(
            "tx-auth:refreshAudience", # for T-System dataspace
            "https://w3id.org/tractusx/auth/refreshAudience",
        )
    )

    refresh_endpoint: str = Field(
        validation_alias=AliasChoices(
            "tx-auth:refreshEndpoint", # for T-System dataspace
            "https://w3id.org/tractusx/auth/refreshEndpoint",
        )
    )

    refresh_token: str = Field(
        validation_alias=AliasChoices(
            "tx-auth:refreshToken", # for T-System dataspace
            "https://w3id.org/tractusx/auth/refreshToken",
        )
    )
