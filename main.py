from fastapi import FastAPI, HTTPException, Response
import uvicorn
from src.cee.sequence_generator import SequenceGenerator
from src.cee.db_handler import (
    DbHandlerExecution,
    DbHandlerNodeExecution,
    DbHandlerWorkflow,
    initialize_database,
)
from src.cee.execution_manager import ExecutionManager
from contextlib import asynccontextmanager
from src.cee.schema.api_schema import ExecRequestInput, GraphInput
from src.cee.schema.db_schema import WorkflowCols
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from src.cee.docker_logs import router as docker_logs_router


execution_manager = ExecutionManager()
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    await execution_manager.start()

    yield

    await execution_manager.stop()


app = FastAPI(
    title="Asset Workflow Backend",
    description="Backend API for Workflow Engine",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(docker_logs_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", # for dev
        "http://127.0.0.1:5173", # for dev
        "http://localhost:8088",
        "http://127.0.0.1:8088",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Workflow Backend is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# --------------------------------------------------------------------
# interface for handling workflow objects
# --------------------------------------------------------------------


@app.post("/workflows")
async def register_workflow(request: GraphInput):
    graph = request.graph_json
    name = request.workflow_name

    try:
        parser = SequenceGenerator(graph)
        if not parser.check_dag():
            raise HTTPException(
                status_code=400, detail="Graph is not Directed Acyclic Graph (DAG)."
            )

        execution_flow = parser.generate_plan()

        result = DbHandlerWorkflow.insert_workflow(name, graph, execution_flow)

        return {
            "workflow_id": result.workflow_id,
            "workflow_name": name,
            "updated_at": result.updated_at,
            "execution_flow": execution_flow,
        }

    except ValueError as e:  # if the graph is ill formatted and cannot be processed
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/workflows/all", response_model=list[WorkflowCols])
async def get_all_workflows():
    return DbHandlerWorkflow.get_all()


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    workflow = DbHandlerWorkflow.get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return workflow


@app.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    success = DbHandlerWorkflow.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return Response(status_code=204)


# --------------------------------------------------------------------
# interface for handling execution objects
# --------------------------------------------------------------------


@app.get("/execution")
async def get_all_executions():
    db = DbHandlerExecution()
    return {"executions": db.get_all_executions()}


@app.post("/execution/request")
async def execution_request(request: ExecRequestInput):
    # reject if the workflow_id does not exist
    workflow_id = request.workflow_id
    workflow = DbHandlerWorkflow.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    # push the execution object into the db table
    result = DbHandlerExecution.insert_execution(workflow_id)

    return {"reference_id": result.reference_id, "workflow_id": workflow_id}


@app.get("/execution/{execution_id}")
async def get_execution(execution_id: str):
    execution = DbHandlerExecution.get_execution(execution_id)

    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "reference_id": execution.reference_id,
        "workflow_id": execution.workflow_id,
        "start_at": execution.start_at,
        "finish_at": execution.finish_at,
        "current_state": execution.current_state,
        "nodes": [
            {
                "node_id": node.node_id,
                "current_state": node.current_state,
                "celery_task_id": node.celery_task_id,
                "error_message": node.error_message,
                "queued_at": node.queued_at,
                "start_at": node.start_at,
                "finish_at": node.finish_at,
            }
            for node in DbHandlerNodeExecution.get_all(execution_id)
        ],
    }


@app.delete("/execution/{execution_id}")
async def cancel_execution(execution_id: str):
    success = execution_manager.cancel_execution(execution_id)

    if not success:
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "message": "Execution cancelled",
        "execution_id": execution_id,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
