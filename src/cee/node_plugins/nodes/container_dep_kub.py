from pydantic import BaseModel, Field
from typing import Literal, Any
from cee.node_plugins.base import Base
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

class ContainerDeploymentKubernetes(Base):
    """Container Deployment Kubernetes node."""

    # Input is always a list of Items
    class InputSpec(BaseModel):
        pass

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        pass

    class ParamSpec(BaseModel):
        """Container Deployment Kubernetes node param spec."""

        deployment_name: str
        replicas: int
        namespace: str

        image_name: str
        image_tag: str
        registry: str | None = None

        image_pull_policy: Literal["Always", "IfNotPresent", "Never"] = Field(
                default="IfNotPresent",
                description="Kubernetes container image pull policy",
            )


    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        super().__init__(node)


    def run(self, config: dict, input_data: dict | None = None) -> None:
        """Run the ndoe."""
        print(f"[Node {self.node_id}] Execution started")

        # ----------------------------------------------------
        # Read parameters
        # ----------------------------------------------------
        deployment_name = self.params['deployment_name']
        replicas = self.params['replicas']
        namespace = self.params['namespace']
        
        image_name = self.params['image_name']
        image_tag = self.params['image_tag']
        registry = self.params['registry']
        image_pull_policy = self.params["image_pull_policy"]

        # ----------------------------------------------------
        # Build full image name
        # ----------------------------------------------------
        if registry:
            full_image_name = f"{registry.rstrip('/')}/{image_name}:{image_tag}"
        else:
            full_image_name = f"{image_name}:{image_tag}"

        # ----------------------------------------------------
        # Connect to Kubernetes
        # ----------------------------------------------------
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()

        # ----------------------------------------------------
        # Create Deployment object
        # ----------------------------------------------------
        container = client.V1Container(
            name=deployment_name,
            image=full_image_name,
            image_pull_policy=image_pull_policy,
        )        

        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={
                    "app": deployment_name,
                }
            ),
            spec=client.V1PodSpec(
                containers=[container],
            ),
        )

        deployment_spec = client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(
                match_labels={
                    "app": deployment_name,
                }
            ),
            template=pod_template,
        )

        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=deployment_name,
            ),
            spec=deployment_spec,
        )

        # ----------------------------------------------------
        # Deploy
        # ----------------------------------------------------       
        try:
            apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment,
            )

            print(
                f"[Node {self.node_id}] Deployment '{deployment_name}' created successfully."
            )

        except ApiException as e:
            if e.status == 409:
                raise RuntimeError(
                    f"Deployment '{deployment_name}' already exists."
                ) from e
            raise

        self.finished = True