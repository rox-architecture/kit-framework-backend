from collections.abc import Callable
from typing import Annotated, Any, Literal

from pydantic import (
    Field,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)

from cee.models.edc.entity import Entity


def _get_serialized_boolean(boolean: bool) -> str:  # noqa: FBT001
    """Return the JSON serialization of the given boolean."""
    if boolean:
        return "true"
    return "false"


def _get_deserialized_boolean(string: str) -> bool:
    """Return the deserialized boolean for the given string."""
    if string == "true":
        return True
    if string == "false":
        return False
    error_message = "Must be 'true' or 'false'"
    raise ValueError(error_message)


class OAuthConfig(Entity):
    """OAuth config model."""

    token_url: str
    client_id: str
    client_secret_key: str


class AmazonDataAddress(Entity):
    """EDC AmazonS3 data address model."""

    type: Literal["AmazonS3"] = "AmazonS3"
    region: str
    endpoint_override: str | None = None
    bucket_name: str
    object_name: str | None = None
    object_prefix: str | None = None
    folder_name: str | None = None
    key_name: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None


class AzureDataAddress(Entity):
    """EDC AzureStorage data address model."""

    type: Literal["AzureStorage"] = "AzureStorage"
    container: str
    account: str
    blob_name: str | None = None
    blob_prefix: str | None = None
    folder_name: str | None = None
    key_name: str


class HttpDataAddress(Entity):
    """EDC HTTP data address model."""

    type: Literal["HttpData"] = "HttpData"
    base_url: str
    method: str = "GET"
    path: str | None = None
    body: Any = None
    query_params: dict[str, str] | None = None
    proxy_method: bool = False
    proxy_path: bool = False
    proxy_body: bool = False
    proxy_query_params: bool = False
    oauth_config: OAuthConfig | None = None
    headers: dict[str, str] | None = None

    @field_validator(
        "proxy_path", "proxy_method", "proxy_body", "proxy_query_params", mode="before"
    )
    @classmethod
    def deserialize_boolean_string(cls, value: Any) -> Any:
        """Deserialize boolean strings."""
        if isinstance(value, str):
            return _get_deserialized_boolean(value)
        return value

    @model_validator(mode="before")
    @classmethod
    def extract_headers_and_oauth_config(cls, data: Any) -> Any:
        """Deserialize headers and OAuth config."""
        if not isinstance(data, dict):
            return data
        oauth_config = {}
        headers = {}

        for key, value in data.items():
            if key.startswith("header:"):
                headers[key[len("header:") :]] = value
            if key.startswith("oauth:"):
                oauth_config[key[len("oauth:") :]] = value

        result = data.copy()
        if bool(headers):
            result["headers"] = headers
        if bool(oauth_config):
            result["oauthConfig"] = oauth_config

        return result

    @field_serializer("proxy_path", "proxy_method", "proxy_body", "proxy_query_params")
    def serialize_boolean_string(self, value: bool) -> str:  # noqa: FBT001
        """Serialize boolean strings."""
        return _get_serialized_boolean(value)

    @model_serializer(mode="wrap")
    def serialize_headers_and_oauth_config(self, handler: Callable[[Any], Any]) -> Any:
        """Serialize headers and OAuth config."""
        data = handler(self)
        assert isinstance(data, dict)

        headers = data.pop("headers", None)
        oauth_config = data.pop("oauthConfig", None)

        if headers is not None:
            for key, value in headers.items():
                data[f"header:{key}"] = value

        if oauth_config is not None:
            for key, value in oauth_config.items():
                data[f"oauth:{key}"] = value

        return data


class ProxyDataAddress(Entity):
    """EDC HTTP proxy data address model."""

    type: Literal["HttpProxy"] = "HttpProxy"


DataAddress = Annotated[
    AmazonDataAddress | AzureDataAddress | HttpDataAddress | ProxyDataAddress,
    Field(discriminator="type"),
]
