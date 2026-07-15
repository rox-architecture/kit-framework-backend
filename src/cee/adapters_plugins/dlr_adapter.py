import os
from functools import lru_cache
from typing import Any

import requests
from pydantic import TypeAdapter

from cee.adapters_plugins.adapter import Adapter
from cee.models.edc import Catalog, Dataset, Edr, EdrDataAddress, NegotiationInitiation

EdrsAdapter = TypeAdapter(list[Edr])

EDC_CONTEXT = {
    "tx": "https://w3id.org/tractusx/v0.0.1/ns/",
    "tx-auth": "https://w3id.org/tractusx/auth/",
    "cx-policy": "https://w3id.org/catenax/2025/9/policy/",
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "dspace": "https://w3id.org/dspace/v0.8/",
}


# This class can interact with the dataspace connector based on Tractus-X
class DlrAdapter(Adapter):
    """Adapter for interaction with the dataspace connector."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.catalog_url = "https://vision-x-api.base-x-ecosystem.org/federated/catalog"
        self.base_url = os.getenv("BASE_URL_DLR_CONNECTOR")
        self.api_key = os.getenv("API_KEY_DLR_CONNECTOR")

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    @lru_cache(maxsize=1)
    def _get_edrs(self) -> list[Edr]:
        """Return all EDRs."""
        endpoint = "cp/management/v3/edrs/request"
        url = f"{self.base_url}/{endpoint}"
        payload = {
            "@context": EDC_CONTEXT,
            "@type": "QuerySpec",
            "offset": 0,
            "limit": 10000,
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return EdrsAdapter.validate_python(response.json())

    def _get_catalog(self, provider_bpn: str, provider_url: str) -> Catalog:
        """Return the catalog for the given provider."""
        endpoint = "cp/management/v3/catalog/request"
        url = f"{self.base_url}/{endpoint}"
        payload = {
            "@context": EDC_CONTEXT,
            "counterPartyAddress": str(provider_url),
            "counterPartyId": provider_bpn,
            "protocol": "dataspace-protocol-http",
            "querySpec": {
                "offset": 0,
                "limit": 10000,
            },
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return Catalog.model_validate(response.json())

    def _get_offer(self, catalog: Catalog, asset_id: str) -> Dataset | None:
        """Return the offer for the asset with the given ID."""
        for dataset in catalog.datasets:
            if dataset.asset_id != asset_id:
                continue
            return dataset
        return None

    def _get_edr_data_address(
        self, edrs: list[Edr], asset_id: str
    ) -> EdrDataAddress | None:
        """Return the EDR data address for the asset with the given ID."""
        for edr in edrs:
            if edr.asset_id != asset_id:
                continue
            endpoint = f"cp/management/v3/edrs/{edr.transfer_process_id}/dataaddress"
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url)
            return EdrDataAddress.model_validate(response.json())
        return None

    # TODO: replace _get_target_offer_by_id with a proper way of fetching the policy
    def _initiate_negotiation(
        self, offer: Dataset, provider_bpn: str, provider_url: str
    ) -> None:
        """Initiate a negotiation for the given offer."""
        policy = offer.policies[0] | {
            "odrl:assigner": {"@id": provider_bpn},
            "odrl:target": {"@id": offer.asset_id},
        }

        payload = NegotiationInitiation(
            at_context=EDC_CONTEXT,
            counter_party_address=str(provider_url),
            protocol="dataspace-protocol-http",
            policy=policy,
        ).model_dump()
        
        endpoint = "cp/management/v3/edrs"
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=payload)
        response.raise_for_status()

    def get_negotiated_assets(self) -> set[str]:
        """Return the IDs of all negotiated assets."""
        return {edr.asset_id for edr in self._get_edrs()}

    def initiate_negotiation(
        self, provider_bpn: str, provider_url: str, asset_id: str
    ) -> None:
        """Initiate a negotiation for the asset with the given ID."""
        catalog = self._get_catalog(provider_bpn, provider_url)
        offer = self._get_offer(catalog, asset_id)

        if offer is None:
            error_message = "Offer not found"
            raise PermissionError(error_message)

        self._initiate_negotiation(offer, provider_bpn, provider_url)

    def transfer_data_pull(
        self,
        asset_id: str,
        *,
        method: str = "GET",
        subpath: str | None = None,
        payload: Any = None,
    ) -> requests.Response:
        """Initiate a PULL transfer for the asset with the given ID."""
        edrs = self._get_edrs()
        data_address = self._get_edr_data_address(edrs, asset_id)

        if data_address is None:
            error_message = "Negotiation required"
            raise PermissionError(error_message)

        url = data_address.endpoint + (subpath or "")
        headers = {"Authorization": data_address.authorization}

        response = requests.request(
            method, url, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        return response
