from pydantic import BaseModel
from cee.adapters_plugins.adapter import Adapter
import os
import requests
from typing import Any


# This class can interact with the dataspace connector based on Tractus-X
class DlrAdapter(Adapter):
    """Adapter for interaction with the dataspace connector."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.base_url = os.getenv("BASE_URL_DLR_CONNECTOR")
        self.api_key = os.getenv("API_KEY_DLR_CONNECTOR")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    # Internal method for returning the EDR (endpoint, access_token), otherwise (None, None)
    def _request_edr(self, asset_id: str) -> tuple[str | None, str | None]:
        """Return the EDR data address for the asset with the given ID."""
        # ---------------------------------
        # STEP 1: obtain the transfer id
        # ---------------------------------
        endpoint = "cp/management/v3/edrs/request"
        url = f"{self.base_url}/{endpoint}"
        payload = {
            "@context": {},
            "@type": "QuerySpec",
            "filterExpression": [
                {"operandLeft": "assetId", "operator": "=", "operandRight": asset_id}
            ],
        }
        response = requests.post(url, json=payload, headers=self.headers)
        if response.json() == []:
            return None, None
        transfer_id = response.json()[0]["transferProcessId"]

        # ---------------------------------
        # STEP 2: return (endpoint, access_token)
        # ---------------------------------
        endpoint = f"cp/management/v3/edrs/{transfer_id}/dataaddress"
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        access_token = response.json()["authorization"]
        endpoint = response.json()["endpoint"]
        return endpoint, access_token

    # TODO: re-implement this without using the federated catalogue
    @staticmethod
    def _get_target_offer_by_id(provider_id: str, asset_id: str) -> dict[str, Any]:
        """Return the offer for the asset with the given ID."""
        response = requests.get(
            url="https://vision-x-api.base-x-ecosystem.org/federated/catalog"
        )
        response.raise_for_status()

        for cat in response.json():
            participant_id = cat["dspace:participantId"]
            originator = cat["originator"]
            if participant_id != provider_id:  # filter out non-matching bpn
                continue
            datasets = cat["dcat:dataset"]
            if not isinstance(datasets, list):  # cast datasets into an array
                datasets = [datasets]
            if not datasets:  # skip if datasets is empty
                continue
            for asset in datasets:
                if asset["@id"] != asset_id:  # not matching id
                    continue

                # if match,
                asset["participantId"] = participant_id
                asset["originator"] = originator
                asset["policy"] = asset["odrl:hasPolicy"]
                return asset
        # if not found
        return {}

    # This internal method make a negotiation given the provider information and asset id
    # TODO: replace _get_target_offer_by_id with a proper way of fetching the policy
    def _make_negotiation(
        self, provider_bpn: str, provider_url: str, asset_id: str
    ) -> requests.Response:
        """Initiate a negotiation for the asset with the given ID."""
        endpoint = "cp/management/v3/edrs"
        url = f"{self.base_url}/{endpoint}"
        offer = self._get_target_offer_by_id(provider_bpn, asset_id)
        
        payload = {
            "@context": {"odrl": "http://www.w3.org/ns/odrl/2/"},
            "counterPartyAddress": str(provider_url),
            "protocol": "dataspace-protocol-http",
            "policy": offer["policy"][0] # TODO: for now we take the first one, otherwise the code crash
            | {
                "odrl:assigner": {"@id": provider_bpn},
                "odrl:target": {"@id": asset_id},
            },
        }

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response

    # Interface method for returning the dataspace asset data
    def transfer_data_pull(
        self,
        provider_bpn: str,
        provider_url: str,
        asset_id: str,
        *,
        auto_nego: bool = True,
    ) -> requests.Response:
        """Initiate a PULL transfer for the asset with the given ID."""
        endpoint, token = self._request_edr(asset_id)

        if endpoint is None and not auto_nego:  # no automatic negotiation disabled
            error_message = "Negotiation required"
            raise PermissionError(error_message)
        if endpoint is None:  # automatic negotiation enabled
            self._make_negotiation(provider_bpn, provider_url, asset_id)
            # try again after negotiation
            endpoint, token = self._request_edr(asset_id)
        
        # pull the http data
        assert endpoint is not None
        header = {"Authorization": token}
        response = requests.get(endpoint, headers=header)
        response.raise_for_status()
        return response
