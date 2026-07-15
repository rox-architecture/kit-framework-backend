from pydantic import BaseModel, HttpUrl
from typing import Literal, Any
from cee.schema.execution_schema import Item
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY


class HttpAssetPublish(Base):
    """Asset Publish node."""

    class InputSpec(BaseModel):
        """Asset Publish node input spec."""
        input_0: Item # metadata + access information

    class ParamSpec(BaseModel):
        """Asset Publish node param spec."""
        adapter_type: str
        asset_id: str
        connector_url: HttpUrl
        

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

        # select the correct adapter based on the parameter value
        adapter_type = self.params["adapter_type"]
        self.adapter = ADAPTER_REGISTRY[adapter_type]()


    def run(self, input_data: dict | None = None) -> None:
        """Run the ndoe."""
        print(f"[Node {self.node_id}] Execution started")

       
        self.finished = True
        
