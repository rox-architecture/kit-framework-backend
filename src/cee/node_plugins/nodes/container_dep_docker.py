from pydantic import BaseModel, Field
from typing import Literal, Any
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY


class ContainerDeploymentDocker(Base):
    """Container Deployment Docker node."""

    class ParamSpec(BaseModel):
        """Container Deployment Docker node param spec."""

        deployment_name: str

        image_name: str
        image_tag: str
        registry: str | None = None


    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)


    def run(self, input_data: dict | None = None) -> None:
        """Run the ndoe."""
        print(f"[Node {self.node_id}] Execution started")

        # ----------------------------------------------------
        # Read parameters
        # ----------------------------------------------------
        image_name = self.params['image_name']
        image_tag = self.params['image_tag']
        registry = self.params['registry']


        # ----------------------------------------------------
        # Build full image name
        # ----------------------------------------------------
        if registry:
            full_image_name = f"{registry.rstrip('/')}/{image_name}:{image_tag}"
        else:
            full_image_name = f"{image_name}:{image_tag}"


        self.finished = True