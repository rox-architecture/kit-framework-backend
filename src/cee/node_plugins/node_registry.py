# dataspace nodes
from cee.node_plugins.nodes.static_file import StaticFile
from cee.node_plugins.nodes.container_image import ContainerImage
from cee.node_plugins.nodes.service_file import ServiceFile
from cee.node_plugins.nodes.service_stream import ServiceStream
from cee.node_plugins.nodes.container_dep_kub import ContainerDeploymentKubernetes
from cee.node_plugins.nodes.zipper import Zipper
from cee.node_plugins.nodes.unzipper import Unzipper
from cee.node_plugins.nodes.send_to_url import SendToUrl
from cee.node_plugins.nodes.http_asset_publish import HttpAssetPublish
from cee.node_plugins.nodes.docker_command import DockerCommand

# Utility nodes
from cee.node_plugins.nodes.save_to_file import SaveToFile

NODE_REGISTRY = {
    # Utility Node Types
    "save_to_file": SaveToFile,
    "container_deployment_kubernetes": ContainerDeploymentKubernetes,
    "zipper": Zipper,
    "unzipper": Unzipper,
    "send_to_url": SendToUrl,
    "docker_command": DockerCommand,

    # Dataspace Node Types
    "ds_static_file": StaticFile,
    "ds_container": ContainerImage,
    "http_asset_publish": HttpAssetPublish,
    "ds_service_file": ServiceFile,
    "ds_service_stream": ServiceStream,
    #TODO "ds_workflow": ...
}
