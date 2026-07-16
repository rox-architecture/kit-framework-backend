from types import SimpleNamespace
from typing import Any

from cee.execution_manager import ExecutionManager


def test_dispatches_child_without_waiting_for_unrelated_branch(
    monkeypatch: Any,
) -> None:
    """A finished fast branch unlocks its child while a sibling still runs."""
    workflow = SimpleNamespace(
        graph_json={
            "nodes": [
                {"id": node_id, "data": {"params": {"type": "unused"}}}
                for node_id in ["root", "slow", "fast", "child"]
            ],
            "edges": [
                {"source": "root", "target": "slow"},
                {"source": "root", "target": "fast"},
                {"source": "fast", "target": "child"},
            ],
        },
        execution_flow={
            "predecessors": {
                "root": [],
                "slow": ["root"],
                "fast": ["root"],
                "child": ["fast"],
            }
        },
    )
    nodes = [
        SimpleNamespace(node_id="root", current_state="FINISHED", celery_task_id="1"),
        SimpleNamespace(node_id="slow", current_state="RUNNING", celery_task_id="2"),
        SimpleNamespace(node_id="fast", current_state="FINISHED", celery_task_id="3"),
        SimpleNamespace(node_id="child", current_state="PENDING", celery_task_id=None),
    ]
    queued: list[str] = []
    sent: list[str] = []

    monkeypatch.setattr(
        "cee.execution_manager.DbHandlerWorkflow.get_workflow", lambda _: workflow
    )
    monkeypatch.setattr(
        "cee.execution_manager.DbHandlerNodeExecution.get_all", lambda _: nodes
    )
    monkeypatch.setattr(
        "cee.execution_manager.DbHandlerNodeExecution.queue",
        lambda _execution, node_id, _task: queued.append(node_id) or True,
    )
    monkeypatch.setattr(
        "cee.execution_manager.celery_app.AsyncResult",
        lambda _task: SimpleNamespace(state="PENDING", result=None),
    )
    monkeypatch.setattr(
        "cee.execution_manager.celery_app.send_task",
        lambda _name, args, **_kwargs: sent.append(args[1]["id"]),
    )

    ExecutionManager()._coordinate("execution", "workflow")  # noqa: SLF001

    assert queued == ["child"]
    assert sent == ["child"]
