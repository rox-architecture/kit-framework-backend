from cee.models.db import Workflow
import asyncio

from cee.db_handler import DbHandlerWorkflow, DbHandlerExecution
from cee.node_plugins.node_registry import NODE_REGISTRY


class ExecutionManager:
    """Manager for executions."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self._task = None
        self._running = False
        self._running_tasks: dict[str, asyncio.Task] = {}  # for the worker cancellation

        self.parameters = {}
        # later, we can add various options to the execution core
        # E.g., "temporary_files": True | False ==> the output of all the nodes are wrapped into list(Item) and saved into a file instead of in the memory.
        # E.g., "parallelisation": True | False ==> the execution of nodes in the same generation can be executed in parallel. Further information will be required.

    async def start(self) -> None:
        """Start the manager."""
        if self._running:
            return

        self._running = True
        print("[ExecutionManager] Started")

        self._task = asyncio.create_task(self.run())

    async def stop(self) -> None:
        """Stop the manager."""
        if not self._running:
            return

        self._running = False
        print("[ExecutionManager] Stopping...")

        if self._task:
            self._task.cancel()

            try:
                await self._task
            except asyncio.CancelledError:
                pass

        print("[ExecutionManager] Stopped")

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
            # Execute the node objects and handle their connections
            # ----------------------------------------------------------------------
            for index, generation in enumerate(
                sequence
            ):  # iterate over the execution sequence
                # for now, all the nodes are sequentially executed
                for node_id in generation:
                    node_obj = executable_nodes[node_id]
                    input_data = {}
                    node_obj.run(input_data)

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
    async def run(self) -> None:
        """Run the manager loop."""
        try:
            while self._running:
                """
                Execution Manager is triggered every 5 seconds.
                """
                # get all the PENDING execution items
                execution_items = DbHandlerExecution.get_executions_by_status("PENDING")

                # for each PENDING execution, assign a worker
                for item in execution_items:
                    workflow_id = item.workflow_id
                    workflow = DbHandlerWorkflow.get_workflow(workflow_id)
                    assert workflow is not None
                    reference_id = str(item.reference_id)
                    # we keep tracking of the workers
                    task = asyncio.create_task(self.run_worker(reference_id, workflow))
                    self._running_tasks[workflow_id] = task

                    task.add_done_callback(
                        lambda _: self._running_tasks.pop(workflow_id, None)
                    )

                print(
                    f"[ExecutionManager] {len(execution_items)} workflow(s) started execution"
                )
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("[ExecutionManager] Cancelled")
            raise
