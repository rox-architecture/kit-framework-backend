from typing import Any, Literal
from pydantic import BaseModel, HttpUrl
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY
import docker 

class DataContainer(Base):
    """Data container node."""

    class ParamSpec(BaseModel):
        """Data file node param spec."""
        adapter_type: str
        provider_bpn: str
        provider_url: HttpUrl
        asset_id: str

        representation: Literal['Dockerfile'] # TODO: add more types like oci-archive, oci-registry
        platforms: set[ Literal['linux/amd64', 'linux/arm64', 'windows/amd64', 'windows/arm64'] ]

        image_name: str
        image_tag: str
        registry_addr: str
        
    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)

        # select the correct adapter based on the parameter value
        adapter_type = self.params["adapter_type"]
        self.adapter = ADAPTER_REGISTRY[adapter_type]()

    def run(self, input_data: dict | None = None) -> None:
        """Run the node."""
        print(f"[Node {self.node_id}] Execution started")

        representation = self.params['representation']

        if representation == 'Dockerfile':
            # receive the Dockerfile from the dataspace
            provider_bpn = self.params['provider_bpn']
            provider_url = self.params['provider_url']
            asset_id = self.params['asset_id']
            response = self.adapter.transfer_data_pull(provider_bpn, provider_url, asset_id)
            # check against the OutputSpec schema and save into a dict

            dockerfile_data = response.content

            registry = self.params['registry_addr']
            image_name = self.params['image_name']
            image_tag = self.params['image_tag']
            full_image_name = f"{registry}/{image_name}:{image_tag}"
            
            # TODO: do I need to write it into the Dockerfile?
            # TODO: how can I register the image to the docker registry v2?
            
            self.finished = True
        

        

