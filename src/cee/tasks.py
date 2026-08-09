"""Celery tasks that execute individual workflow nodes."""

from typing import Any

from cee.artifact_store import FileArtifactStore
from cee.celery_app import celery_app
from cee.db_handler import DbHandlerExecution, DbHandlerNodeExecution
from cee.node_plugins.node_registry import NODE_REGISTRY
from cee.schema.execution_schema import Item


@celery_app.task(name="cee.execute_node", autoretry_for=())  # type: ignore[untyped-decorator]
def execute_node(
    execution_id: str,
    node: dict[str, Any],
    ingress_edges: list[dict[str, str]],
) -> dict[str, Any]:
    """Execute one node and persist its outputs in shared artifact storage."""
    node_id = str(node["id"])
    if DbHandlerExecution.current_state(execution_id) == "CANCELLED":
        return {"execution_id": execution_id, "node_id": node_id, "cancelled": True}
    if not DbHandlerNodeExecution.start(execution_id, node_id):
        return {"execution_id": execution_id, "node_id": node_id, "ignored": True}

    store = FileArtifactStore()
    try:
        input_data: dict[str, Item] = {}
        for edge in ingress_edges:
            if edge["sourceHandle"] == "dep" and edge["targetHandle"] == "dep":
                continue

            reference = store.reference(
                execution_id, str(edge["source"]), str(edge["sourceHandle"])
            )
            input_data[str(edge["targetHandle"])] = store.get(reference)

        node_type = str(node["data"]["params"]["type"])
        node_class: Any = NODE_REGISTRY[node_type]
        node_obj = node_class(node)
        node_obj.run(input_data)
        node_obj.OutputSpec(**node_obj.outputs)

        references: dict[str, str] = {}
        for port, raw_item in node_obj.outputs.items():
            item = (
                raw_item
                if isinstance(raw_item, Item)
                else Item.model_validate(raw_item)
            )
            references[str(port)] = store.put(execution_id, node_id, str(port), item)

        if not DbHandlerNodeExecution.finish(execution_id, node_id):
            return {"execution_id": execution_id, "node_id": node_id, "ignored": True}
        return {  # noqa: TRY300
            "execution_id": execution_id,
            "node_id": node_id,
            "outputs": references,
        }
    except Exception as error:
        DbHandlerNodeExecution.fail(execution_id, node_id, str(error))
        raise
