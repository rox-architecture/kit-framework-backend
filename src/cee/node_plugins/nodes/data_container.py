from typing import Any, Literal
from pydantic import BaseModel, HttpUrl
from cee.node_plugins.base import Base
from cee.adapters_plugins.adapter_registry import ADAPTER_REGISTRY
import docker
import tempfile
from pathlib import Path


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
        registry_addr: str | None = None
        
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
            dockerfile_content = response.content

            # start building the docker container image
            client = docker.from_env()

            image_name = self.params['image_name']
            image_tag = self.params['image_tag']
            
            if "registry_addr" in self.params:
                registry = self.params['registry_addr']
                full_image_name = f"{registry}/{image_name}:{image_tag}"
                push = True
            else:
                full_image_name = f"{image_name}:{image_tag}"
                push = False

            # save Dockerfile in the temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                context = Path(tmpdir)

                dockerfile = context / "Dockerfile"
                dockerfile.write_text(dockerfile_content, encoding="utf-8")

                image, build_logs = client.images.build(
                    path=str(context),
                    dockerfile="Dockerfile",
                    tag=full_image_name,
                    rm=True,
                )

                # print out the image building status 
                print(f"[Node {self.node_id}] Building the container image")
                for log in build_logs:
                    if "stream" in log:
                        for line in log["stream"].splitlines():
                            if line:
                                print(f"[Node {self.node_id}] {line}")

            if push:
                print(f"[Node {self.node_id}] Pushing the container image {full_image_name}...")

                push_logs = client.images.push(
                    repository=f"{registry}/{image_name}",
                    tag=image_tag,
                    stream=True,
                    decode=True,
                )

                for log in push_logs:
                    if "status" in log:
                        message = log["status"]
                        if "progress" in log:
                            message += f" {log['progress']}"
                        print(f"[Node {self.node_id}] {message}")

                    elif "aux" in log:
                        print(f"[Node {self.node_id}] {log['aux']}")

                    elif "error" in log:
                        print(f"[Node {self.node_id}] ERROR: {log['error']}")

                    else:
                        print(f"[Node {self.node_id}] {log}")

            self.finished = True
        

        

