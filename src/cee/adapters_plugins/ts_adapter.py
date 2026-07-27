import os
from typing import Any
from functools import lru_cache
import requests
from pydantic import TypeAdapter

from cee.adapters_plugins.adapter import Adapter
from cee.models.edc import (
    AssetCreation,
    AssetsSelector,
    Catalog,
    DataAddress,
    Dataset,
    Edr,
    EdrDataAddress,
    NegotiationInitiation,
)

FederatedCatalogAdapter = TypeAdapter(list[Catalog])
EdrsAdapter = TypeAdapter(list[Edr])

EDC_CONTEXT = {
    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
    "edc": "https://w3id.org/edc/v0.0.1/ns/",
    "tx": "https://w3id.org/tractusx/v0.0.1/ns/",   
    "tx-auth": "https://w3id.org/tractusx/auth/",
    "cx-policy": "https://w3id.org/catenax/policy/",
    "dct": "http://purl.org/dc/terms/type/",
    "odrl": "http://www.w3.org/ns/odrl/2/",
    "dspace": "https://w3id.org/dspace/v0.8/",
    "cx-common:": "https://w3id.org/catenax/toxonomy#",
    "aas-sematics": "https://admin-shell.io/aas/3/0/HasSemantics"
}

class TsAdapter(Adapter):
    """Adapter for interaction with the dataspace connector."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.base_url = os.getenv("BASE_URL_TS_CONNECTOR")
        self.api_key = os.getenv("API_KEY_TS_CONNECTOR")

        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        })


    def _get_edrs(self) -> list[Edr]:
        """Return all EDRs."""
        endpoint = "data/v2/edrs/request"
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


    def _get_offer(
        self, provider_url: str, provider_id: str, asset_id: str
    ) -> Dataset | None:
        endpoint = "data/v2/catalog/request"
        url = f"{self.base_url}/{endpoint}"
        payload = {
            "@context": EDC_CONTEXT,
            "@type": "CatalogRequest",
            "protocol": "dataspace-protocol-http",
            "counterPartyId": provider_id,
            "counterPartyAddress": f"{str(provider_url).rstrip('/')}/api/v1/dsp",
            "querySpec": {
                "offset": 0,
                "limit": 20000,
                "sortField": "target",
                "sortOrder": "DESC",
                "filterExpression": []
            }
        }

        # response is the catalog
        response = self.session.post(url, json=payload)
        response.raise_for_status()

        for dataset in response.json()['dcat:dataset']:
            if dataset["@id"] == asset_id:
                return Dataset.model_validate(dataset)
        
        return None

    def _initiate_negotiation(
        self, offer: Dataset, provider_bpn: str, provider_url: str
    ) -> None:
        """Initiate a negotiation for the given offer."""
        policy = offer.policies[0] | {
            "odrl:assigner": {"@id": provider_bpn},
            "odrl:target": {"@id": offer.asset_id},
        }
        payload = NegotiationInitiation(
            at_type="ContractRequest",
            at_context=EDC_CONTEXT,
            counter_party_address=f"{str(provider_url).rstrip('/')}/api/v1/dsp",
            protocol="dataspace-protocol-http",
            policy=policy,
        ).model_dump(by_alias=True, exclude_none=True)

        endpoint = "data/v2/edrs"
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=payload)
        response.raise_for_status()


    def create_asset(
        self, asset_id: str, properties: dict[str, Any], data_address: DataAddress
    ) -> None:
        """Create the given asset."""
        payload = AssetCreation(
            at_context=EDC_CONTEXT,
            at_id=asset_id,
            properties=properties,
            data_address=data_address
        ).model_dump(exclude_none=True)

        endpoint = "data/v3/assets"
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=payload)
        response.raise_for_status()

    def _get_edr_data_address(
        self, edrs: list[Edr], asset_id: str
    ) -> EdrDataAddress | None:
        """Return the EDR data address for the asset with the given ID."""
        for edr in edrs:
            if edr.asset_id != asset_id:
                continue
            endpoint = f"data/v2/edrs/{edr.transfer_process_id}/dataaddress?auto_refresh=true"
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url)
            return EdrDataAddress.model_validate(response.json())
        return None

    def get_negotiated_assets(self) -> set[str]:
        """Return the IDs of all negotiated assets."""
        return {edr.asset_id for edr in self._get_edrs()}

    def initiate_negotiation(
        self, provider_bpn: str, provider_url: str, asset_id: str
    ) -> None:
        """Initiate a negotiation for the asset with the given ID."""
        offer = self._get_offer(provider_url, provider_bpn, asset_id)
    
        if offer is None:
            error_message = "Offer not found"
            raise PermissionError(error_message)
        self._initiate_negotiation(offer, provider_bpn, provider_url)
        

    # TODO: edr token expiration problem needs to be resolved 
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

        # TODO: if authorization is expired then use the refresh url to get the new value and attempt again
        response.raise_for_status()
        return response
