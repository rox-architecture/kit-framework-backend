from pydantic import BaseModel, HttpUrl
from typing import Literal, Any
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY


class DataFile(Base):
    """Data file node."""

    # Predefined Output specification
    class OutputSpec(BaseModel):
        """Data file node output spec."""

        data: Item

    class ParamSpec(BaseModel):
        """Data file node param spec."""
        adapter_type: str
        provider_bpn: str
        provider_url: HttpUrl
        asset_id: str
        access_mode: Literal["pull", "push"]

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

        # select the correct adapter based on the parameter value
        adapter_type = self.params["adapter_type"]
        self.adapter = ADAPTER_REGISTRY[adapter_type]()

    # Implement DataFile node behaviour
    # the outputs are stored in `self.outputs` and retrieved via the Get method
    def run(self, input_data: dict | None = None) -> None:
        """Run the ndoe."""
        print("DataFile node triggered")

        # read parameter values
        provider_bpn = self.params["provider_bpn"]
        provider_url = self.params["provider_url"]
        asset_id = self.params["asset_id"]

        data = self.adapter.transfer_data_pull()

        self.output = {}
