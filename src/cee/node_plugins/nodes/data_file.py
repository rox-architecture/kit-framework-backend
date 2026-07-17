from pydantic import BaseModel, HttpUrl
from typing import Literal, Any
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY


class DataFile(Base):
    """Data file node."""

    # Input is always a list of Items
    class InputSpec(BaseModel):
        pass

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        output_0: Item

    class ParamSpec(BaseModel):
        """Data file node param spec."""
        adapter_type: str
        provider_bpn: str
        provider_url: HttpUrl
        asset_id: str
        #TODO: access_mode: Literal['pull', 'push']

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

        # select the correct adapter based on the parameter value
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
        provider_bpn = self.params['provider_bpn']
        provider_url = self.params['provider_url']
        asset_id = self.params['asset_id']
        
        try:
            response = self.adapter.transfer_data_pull(asset_id)
        except Exception:
            if config['auto_nego']: 
                print("automatic negotiation is triggered")
                ack = self.adapter.initiate_negotiation(provider_bpn, provider_url, asset_id)
                response = self.adapter.transfer_data_pull(asset_id)
            else:
                raise PermissionError("Negotiation required and auto-nego is disabled")
        
        # check against the OutputSpec schema and save into a dict
        data = Item(
            json_data={
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length"),
                "source": { 
                    "provider_url": provider_url,
                    "provider_bpn": provider_bpn,
                    "asset_id": asset_id
                },
            },
            binary=response.content,
        ).model_dump()

        # set 'data' as the output at port index 0
        self.set_output(port=0, item=data)
        self.finished = True
        
