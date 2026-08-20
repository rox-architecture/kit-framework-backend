# dataspace nodes
from cee.node_plugins.dlr_dataspace.static_file import StaticFile as StaticFileDLR
from cee.node_plugins.dlr_dataspace.container_image import ContainerImage as ContainerDLR
from cee.node_plugins.dlr_dataspace.service_file import ServiceFile as ServiceFileDLR
from cee.node_plugins.dlr_dataspace.service_stream import ServiceStream as ServiceStreamDLR
from cee.node_plugins.dlr_dataspace.http_asset_publish import HttpAssetPublish as HttpAssetPublishDLR

# General nodes
from cee.node_plugins.general.zipper import Zipper
from cee.node_plugins.general.unzipper import Unzipper
from cee.node_plugins.general.send_to_url import SendToUrl
from cee.node_plugins.general.save_to_file import SaveToFile

# Deployment nodes
from cee.node_plugins.deployment.container_dep_kub import ContainerDeploymentKubernetes
from cee.node_plugins.deployment.docker_command import DockerCommand

NODE_REGISTRY = {
    # General
    "save_to_file": SaveToFile,
    "zipper": Zipper,
    "unzipper": Unzipper,
    "send_to_url": SendToUrl,

    # DLR Dataspace
    "dlr.static_file": StaticFileDLR,
    "dlr.container": ContainerDLR,
    "dlr.service_file": ServiceFileDLR,
    "dlr.service_stream": ServiceStreamDLR,
    "dlr.create_asset_http": HttpAssetPublishDLR,
    #TODO "ds_workflow": ...

    # Deployment
    "container_deployment_kubernetes": ContainerDeploymentKubernetes,
    "docker_command": DockerCommand,

    # TSI dataspace
    #TODO more...

}
