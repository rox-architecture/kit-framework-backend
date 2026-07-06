from abc import ABC, abstractmethod
from pydantic import BaseModel
import requests


# This is an interface class to establish standardised interface for every adapter
# In this way, the connectors from different dataspace can be used in the same way
# It will allow us to switch between connectors, to do the conceptually same task
class Adapter(ABC):
    """Abstract adapter."""

    @abstractmethod
    def transfer_data_pull(
        self,
        provider_bpn: str,
        provider_url: str,
        asset_id: str,
        *,
        auto_nego: bool = True,
    ) -> requests.Response:
        ...