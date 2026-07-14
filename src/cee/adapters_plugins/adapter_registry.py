# dataspace nodes
from cee.adapters_plugins.dlr_adapter import DlrAdapter
from cee.adapters_plugins.ts_adapter import TsAdapter

ADAPTER_REGISTRY = {
    "dlr_connector": DlrAdapter,
    "ts_connector": TsAdapter
}
