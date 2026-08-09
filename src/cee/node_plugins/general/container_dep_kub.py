"""Optional Kubernetes deployment node for a Docker-hosted worker."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from kubernetes import client, config as kube_config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException
from pydantic import BaseModel, Field

from cee.node_plugins.base import Base


class ContainerDeploymentKubernetes(Base):
    """Create a Kubernetes Deployment when kubeconfig is available."""

    class InputSpec(BaseModel):
        """Kubernetes deployment node input spec."""

        pass

    class OutputSpec(BaseModel):
        """Kubernetes deployment node output spec."""

        pass

    class ParamSpec(BaseModel):
        """Kubernetes deployment node parameter specification."""

        deployment_name: str = Field(min_length=1)
        replicas: int = Field(ge=0)
        namespace: str = Field(min_length=1)

        image_name: str = Field(min_length=1)
        image_tag: str = Field(min_length=1)
        registry: str | None = None

        image_pull_policy: Literal[
            "Always",
            "IfNotPresent",
            "Never",
        ] = Field(
            default="IfNotPresent",
            description="Kubernetes container image pull policy",
        )

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the node."""
        super().__init__(node)

    def _load_kubernetes_configuration(self) -> Path:
        """Load kubeconfig explicitly mounted into the Docker worker."""
        kubeconfig_value = os.environ.get("KUBECONFIG")

        if not kubeconfig_value:
            raise RuntimeError(
                f"[Node {self.node_id}] Kubernetes deployment is unavailable: "
                "KUBECONFIG is not configured for the worker. If Kubernetes "
                "support is required, mount a kubeconfig file into the worker "
                "and set the KUBECONFIG environment variable."
            )

        kubeconfig_path = Path(kubeconfig_value)

        if not kubeconfig_path.is_file():
            raise RuntimeError(
                f"[Node {self.node_id}] Kubernetes configuration file was not "
                f"found: {kubeconfig_path}"
            )

        try:
            kube_config.load_kube_config(config_file=str(kubeconfig_path))
        except ConfigException as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Failed to load Kubernetes "
                f"configuration: {kubeconfig_path}"
            ) from error

        return kubeconfig_path

    def run(self, input_data: dict | None = None) -> None:
        """Create the configured Kubernetes Deployment."""
        print(f"[Node {self.node_id}] Execution started", flush=True)

        self.InputSpec.model_validate(input_data or {})
        params = self.ParamSpec.model_validate(self.params)

        registry = params.registry.rstrip("/") if params.registry else None
        full_image_name = (
            f"{registry}/{params.image_name}:{params.image_tag}"
            if registry
            else f"{params.image_name}:{params.image_tag}"
        )

        kubeconfig_path = self._load_kubernetes_configuration()
        print(
            f"[Node {self.node_id}] Loaded Kubernetes configuration from "
            f"{kubeconfig_path}",
            flush=True,
        )

        apps_v1 = client.AppsV1Api()
        labels = {"app": params.deployment_name}

        container = client.V1Container(
            name=params.deployment_name,
            image=full_image_name,
            image_pull_policy=params.image_pull_policy,
        )

        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=labels),
            spec=client.V1PodSpec(containers=[container]),
        )

        deployment_spec = client.V1DeploymentSpec(
            replicas=params.replicas,
            selector=client.V1LabelSelector(match_labels=labels),
            template=pod_template,
        )

        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=params.deployment_name,
                namespace=params.namespace,
            ),
            spec=deployment_spec,
        )

        try:
            apps_v1.create_namespaced_deployment(
                namespace=params.namespace,
                body=deployment,
            )
        except ApiException as error:
            if error.status == 409:
                raise RuntimeError(
                    f"[Node {self.node_id}] Deployment "
                    f"{params.deployment_name!r} already exists in namespace "
                    f"{params.namespace!r}."
                ) from error

            raise RuntimeError(
                f"[Node {self.node_id}] Kubernetes API rejected the deployment "
                f"request (status={error.status}, reason={error.reason})."
            ) from error
        except Exception as error:
            raise RuntimeError(
                f"[Node {self.node_id}] Could not reach or communicate with "
                "the Kubernetes cluster. Check the kubeconfig API server "
                "address, network access, credentials, and permissions."
            ) from error

        print(
            f"[Node {self.node_id}] Deployment {params.deployment_name!r} "
            f"created successfully in namespace {params.namespace!r} using "
            f"image {full_image_name!r}.",
            flush=True,
        )
        self.finished = True
