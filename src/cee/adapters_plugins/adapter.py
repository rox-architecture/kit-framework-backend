from abc import ABC, abstractmethod
from typing import Any

import requests


# This is an interface class to establish standardised interface for every adapter
# In this way, the connectors from different dataspace can be used in the same way
# It will allow us to switch between connectors, to do the conceptually same task
class Adapter(ABC):
    """Abstract adapter."""

    @abstractmethod
    def get_negotiated_assets(self) -> set[str]:
        """Return the IDs of all negotiated assets."""

    @abstractmethod
    def initiate_negotiation(
        self, provider_bpn: str, provider_url: str, asset_id: str
    ) -> None:
        """Initiate a negotiation for the asset with the given ID."""

    @abstractmethod
    def transfer_data_pull(
        self,
        asset_id: str,
        *,
        method: str = "GET",
        subpath: str | None = None,
        payload: Any = None,
    ) -> requests.Response:
        """Initiate a PULL transfer for the asset with the given ID."""
