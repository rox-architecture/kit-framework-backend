from typing import Any

from pydantic import BaseModel, HttpUrl

from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY
from cee.node_plugins.base import Base
from cee.schema.execution_schema import Item


class ServiceFile(Base):
    """Service file node."""

    # Predefined Input specification
    class InputSpec(BaseModel):
        """Service file node input spec."""

        adapter_type: str
        provider_bpn: str
        provider_url: HttpUrl
        asset_id: str
        method: str = "GET"
        subpath: str | None = None
        payload: Any = None

    # Predefined Output specification
    class OutputSpec(BaseModel):
        """Service file node output spec."""

        output_0: Item

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

        adapter_type = self.params["adapter_type"]
        self.adapter = ADAPTER_REGISTRY[adapter_type]()

    def check_validty(self) -> bool:
        """Check whether the node is valid."""
        asset_id = self.params["asset_id"]
        return asset_id in self.adapter.get_negotiated_assets()

    # Implement DataFile node behaviour
    # the outputs are stored in `self.outputs` and retrieved via the Get method
    def run(self, config: dict, input_data: dict | None = None) -> None:
        """Run the ndoe."""
        print(f"[Node {self.node_id}] Execution started")

        # read parameter values
        provider_bpn = self.params["provider_bpn"]
        provider_url = self.params["provider_url"]
        asset_id = self.params["asset_id"]
        method = self.params["method"]
        subpath = self.params["subpath"]
        payload = self.params["payload"]

        try:
            response = self.adapter.transfer_data_pull(
                asset_id, method=method, subpath=subpath, payload=payload
            )
        except Exception:
            if config['auto_nego']: 
                print("automatic negotiation is triggered")
                ack = self.adapter.initiate_negotiation(
                    provider_bpn, provider_url, asset_id
                )
                response = self.adapter.transfer_data_pull(asset_id)
            else:
                raise PermissionError("Negotiation required and auto-nego is disabled")
            
            
        data = Item(
            json_data={
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
                "source": {
                    "provider_url": provider_url,
                    "provider_bpn": provider_bpn,
                    "asset_id": asset_id,
                },
            },
            binary=response.content,
        ).model_dump()

        self.set_output(port=0, item=data)
        self.finished = True
