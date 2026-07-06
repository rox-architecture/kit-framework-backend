# dataspace nodes
from cee.node_plugins.nodes.data_file import DataFile
from cee.node_plugins.nodes.data_container import DataContainer
from cee.node_plugins.nodes.software_file import SoftwareFile
from cee.node_plugins.nodes.software_container import SoftwareContainer
from cee.node_plugins.nodes.service_file import ServiceFile
from cee.node_plugins.nodes.service_stream import ServiceStream

# Utility nodes
from cee.node_plugins.nodes.save_to_file import SaveToFile

NODE_REGISTRY = {
    # Utility Node Types
    "save_to_file": SaveToFile,
    # Dataspace Node Types
    "data_file": DataFile,
    "data_container": DataContainer,
    "software_file": SoftwareFile,
    "software_container": SoftwareContainer,
    "service_file": ServiceFile,
    "service_stream": ServiceStream,
}
