import asyncio
from src.db_handler import DbHandlerWorkflow, DbHandlerExecution
from datetime import datetime, UTC

class ExecutionManager:
    def __init__(self):
        self._task = None
        self._running = False

        # for each schedule item, we assign one async task
        self._running_tasks: dict[str, asyncio.Task] = {}

    async def start(self):
        if self._running:
            return

        self._running = True
        print("[ExecutionManager] Started")

        self._task = asyncio.create_task(self.run())

    async def stop(self):
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
    async def run_worker(self, reference_id: str, workflow: dict):
        execution_db = DbHandlerExecution()

        graph = workflow['graph_json']
        sequence = workflow['execution_flow']
        
        try:
            print(f"[Worker] Start workflow {reference_id}")
            execution_db.execution_started(reference_id)

            await asyncio.sleep(10)

        except asyncio.CancelledError:
            print(f"[Worker] Cancelled workflow {reference_id}")
            execution_db.execution_cancelled(reference_id)
            raise

        except Exception as e:
            print(f"[Worker] Failed workflow {reference_id}: {e}")
            execution_db.execution_failed(reference_id)


        finally:
            print(f"[Worker] Finished workflow {reference_id}")
            execution_db.execution_finished(reference_id)


    # This is the main loop of the execution manager
    # The schedule db is monitored 
    async def run(self):
        try:
            execution_db = DbHandlerExecution()
            workflow_db = DbHandlerWorkflow()

            while self._running:
                """
                Execution Manager is triggered every 5 seconds.
                """
                # get all the PENDING execution items
                execution_items = execution_db.get_executions_by_status("PENDING")
                
                # for each PENDING execution, assign a worker
                for item in execution_items:
                    workflow_id = item['workflow_id']
                    workflow = workflow_db.get_workflow(workflow_id)
                    reference_id = item['reference_id']
                    # we keep tracking of the workers
                    self._running_tasks[workflow_id] = asyncio.create_task(self.run_worker(reference_id, workflow))
               
                print(f"[ExecutionManager] {len(execution_items)} workflow(s) started execution")
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("[ExecutionManager] Cancelled")
            raise