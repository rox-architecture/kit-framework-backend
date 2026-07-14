# dataspace nodes
from cee.node_plugins.nodes.data_file import DataFile
from cee.node_plugins.nodes.container_image import ContainerImage
from cee.node_plugins.nodes.software_file import SoftwareFile
from cee.node_plugins.nodes.service_file import ServiceFile
from cee.node_plugins.nodes.service_stream import ServiceStream
from cee.node_plugins.nodes.container_dep_kub import ContainerDeploymentKubernetes
from cee.node_plugins.nodes.zipper import Zipper

# Utility nodes
from cee.node_plugins.nodes.save_to_file import SaveToFile

NODE_REGISTRY = {
    # Utility Node Types
    "save_to_file": SaveToFile,
    "container_deployment_kubernetes": ContainerDeploymentKubernetes,
    "zipper": Zipper,

    # Dataspace Node Types
    "data_file": DataFile,
    "container_image": ContainerImage,
    "software_file": SoftwareFile,
    "service_file": ServiceFile,
    "service_stream": ServiceStream,
}
