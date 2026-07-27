"""Dependency-aware workflow execution coordinator."""

import asyncio
import contextlib
import time
import uuid
from typing import Any

from cee.artifact_store import FileArtifactStore
from cee.celery_app import celery_app
from cee.config import (
    ARTIFACT_RETENTION,
    RETAIN_FAILED_ARTIFACTS,
    SCHEDULER_POLL_INTERVAL,
)
from cee.db_handler import (
    DbHandlerExecution,
    DbHandlerNodeExecution,
    DbHandlerWorkflow,
)
from cee.sequence_generator import SequenceGenerator


class ExecutionManager:
    """Claim executions and dispatch dependency-ready nodes to Celery."""

    def __init__(self) -> None:
        """Initialize an inactive coordinator."""
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._cleanup_after: dict[str, float] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}  # for the worker cancellation

        # TODO: add more configuration aspects
        self.configurations = {
            "auto_nego": True, # automatically make required negotiations
            "auto_nego_retry_wait_sec": 5, # wait each negotiation attempt for 5 seconds
            "auto_nego_retry_count": 3,
        } 

    async def set_config(self, config_changes):
        self.configurations.update(config_changes)
        return self.configurations

    async def start(self) -> None:
        """Start the coordinator polling loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        """Stop the coordinator polling loop."""
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel queued work without terminating tasks already running."""
        if not DbHandlerExecution.execution_cancelled(execution_id):
            return False
        nodes = DbHandlerNodeExecution.get_all(execution_id)
        for node in nodes:
            if node.current_state == "QUEUED" and node.celery_task_id:
                celery_app.control.revoke(node.celery_task_id, terminate=False)
        DbHandlerNodeExecution.cancel_unfinished(execution_id)
        self._schedule_cleanup(execution_id, "CANCELLED")
        return True


    # TODO: this part is where the workflow is executed by the worker
    async def run_worker(self, reference_id: str, workflow: Workflow) -> None:
        """Run the given workflow in a worker."""
        failed = False
        graph = workflow.graph_json
        sequence = workflow.execution_flow

        try:
            print(f"[Execution {reference_id}] Start workflow")
            DbHandlerExecution.execution_started(reference_id)

            # ----------------------------------------------------------------------
            # Construct executable objects for every node in the graph
            # ----------------------------------------------------------------------
            executable_nodes = {}
            for node in graph["nodes"]:
                node_id = node["id"]
                node_type = node["data"]["params"]["type"]
                node_class = NODE_REGISTRY[
                    node_type
                ]  # select the correct node class from the registry
                print(f"[Execution {reference_id}]", end=" ")
                executable_nodes[node_id] = node_class(
                    node
                )  # instantiate the node object

            # ----------------------------------------------------------------------
            # Check the workflow validity (executability)
            # ----------------------------------------------------------------------

            # TODO: store the nodes requiring negotiation to inform the user later
            # nego_required_nodes = []
            # if not self.configurations['auto_nego']:
            #     for node in executable_nodes.values():
            #         if not node.check_validty():
            #             error_message = "Negotiation is required while auto-nego is disabled"
            #             raise ValueError(error_message)
                    
            # ----------------------------------------------------------------------
            # Execute the node objects and handle their connections
            # ----------------------------------------------------------------------
            for index, generation in enumerate(sequence): # iterate over the execution sequence
                # sequential node execution 
                # TODO: parallelisation
                for node_id in generation:
                    # this is the current node to execute
                    node_obj = executable_nodes[node_id]

                    # the node needs input data to execute
                    ingress_edges = [e for e in graph['edges'] if e['target'] == node_id]
                    input_data = {}

                    # collect the input_data required
                    for e in ingress_edges:
                        # find out the source node and port information
                        predescent_node_id = e['source']
                        source_port_ref = e['sourceHandle']

                        # get the predescent node executable object to get the output Item
                        predescent_node_obj = executable_nodes[predescent_node_id]
                        item = predescent_node_obj.get_output(source_port_ref)

                        # if no output is available from the source node
                        if item is None:
                            continue

                        # find out which input port this Item is connected
                        target_port_ref = e['targetHandle']
                        input_data[target_port_ref] = item

                    # execute the node in a non-blocking way
                    await asyncio.to_thread(node_obj.run, self.configurations, input_data)


        except asyncio.CancelledError:
            print(f"[Execution {reference_id}] Cancelled workflow {reference_id}")
            DbHandlerExecution.execution_cancelled(reference_id)
            raise

        except Exception as e:
            print(f"[Execution {reference_id}] Failed workflow {reference_id}: {e}")
            DbHandlerExecution.execution_failed(reference_id)
            failed = True

        finally:
            if not failed:
                print(f"[Execution {reference_id}] Finished workflow {reference_id}")
                DbHandlerExecution.execution_finished(reference_id)

    # This is the main loop of the execution manager
    # The schedule db is monitored
>>>>>>> src/cee/execution_manager.py
    async def run(self) -> None:
        """Continuously claim executions and advance ready nodes."""
        while self._running:
            for execution_id in DbHandlerExecution.claim_pending():
                self._initialize_execution(execution_id)

            for execution in DbHandlerExecution.get_executions_by_status("RUNNING"):
                self._coordinate(
                    str(execution.reference_id), str(execution.workflow_id)
                )

            self._cleanup_expired()
            await asyncio.sleep(SCHEDULER_POLL_INTERVAL)

    def _initialize_execution(self, execution_id: str) -> None:
        execution = DbHandlerExecution.get_execution(execution_id)
        if execution is None:
            return
        workflow = DbHandlerWorkflow.get_workflow(str(execution.workflow_id))
        if workflow is None:
            DbHandlerExecution.execution_failed(execution_id)
            return
        node_ids = [str(node["id"]) for node in workflow.graph_json.get("nodes", [])]
        DbHandlerNodeExecution.initialize(execution_id, node_ids)

    def _coordinate(  # noqa: C901
        self, execution_id: str, workflow_id: str
    ) -> None:
        workflow = DbHandlerWorkflow.get_workflow(workflow_id)
        if workflow is None:
            DbHandlerExecution.execution_failed(execution_id)
            return

        graph: dict[str, Any] = workflow.graph_json
        node_by_id = {str(node["id"]): node for node in graph.get("nodes", [])}
        nodes = DbHandlerNodeExecution.get_all(execution_id)
        if len(nodes) != len(node_by_id):
            DbHandlerNodeExecution.initialize(execution_id, list(node_by_id))
            nodes = DbHandlerNodeExecution.get_all(execution_id)
        states = {node.node_id: node.current_state for node in nodes}

        self._synchronize_celery_failures(execution_id, nodes)
        nodes = DbHandlerNodeExecution.get_all(execution_id)
        states = {node.node_id: node.current_state for node in nodes}

        if any(state == "FAILED" for state in states.values()):
            DbHandlerExecution.execution_failed(execution_id)
            self._schedule_cleanup(execution_id, "FAILED")
            return
        if states and all(state == "FINISHED" for state in states.values()):
            DbHandlerExecution.execution_finished(execution_id)
            self._schedule_cleanup(execution_id, "FINISHED")
            return
        if not states:
            DbHandlerExecution.execution_finished(execution_id)
            self._schedule_cleanup(execution_id, "FINISHED")
            return

        execution_flow = workflow.execution_flow
        if not isinstance(execution_flow, dict):
            execution_flow = SequenceGenerator(graph).generate_plan()
        predecessors = execution_flow.get("predecessors", {})
        edges = graph.get("edges", [])
        for node_id, state in states.items():
            dependencies = [str(value) for value in predecessors.get(node_id, [])]
            if state != "PENDING" or not all(
                states.get(dependency) == "FINISHED" for dependency in dependencies
            ):
                continue
            task_id = str(uuid.uuid4())
            if not DbHandlerNodeExecution.queue(execution_id, node_id, task_id):
                continue
            ingress = [edge for edge in edges if str(edge["target"]) == node_id]
            try:
                celery_app.send_task(
                    "cee.execute_node",
                    args=[execution_id, node_by_id[node_id], ingress],
                    task_id=task_id,
                )
            except Exception as error:
                DbHandlerNodeExecution.fail(execution_id, node_id, str(error))

    @staticmethod
    def _synchronize_celery_failures(execution_id: str, nodes: list[Any]) -> None:
        for node in nodes:
            if (
                node.current_state not in {"QUEUED", "RUNNING"}
                or not node.celery_task_id
            ):
                continue
            result = celery_app.AsyncResult(node.celery_task_id)
            if result.state in {"FAILURE", "REVOKED"}:
                message = str(result.result) if result.result else result.state
                DbHandlerNodeExecution.fail(execution_id, node.node_id, message)

    def _schedule_cleanup(self, execution_id: str, state: str) -> None:
        if state == "FAILED" and RETAIN_FAILED_ARTIFACTS:
            return
        self._cleanup_after.setdefault(
            execution_id, time.monotonic() + ARTIFACT_RETENTION
        )

    def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [
            key for key, deadline in self._cleanup_after.items() if deadline <= now
        ]
        store = FileArtifactStore()
        for execution_id in expired:
            store.delete_execution(execution_id)
            self._cleanup_after.pop(execution_id, None)
