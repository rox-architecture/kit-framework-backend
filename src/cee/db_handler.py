from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session

from cee.models.db import Base, Workflow, Execution

engine = create_engine(
    "postgresql+psycopg://admin:admin@localhost:5432/workflowdb",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

Base.metadata.create_all(engine)


class DbHandlerWorkflow:
    """Database handler for workflows."""

    @staticmethod
    def insert_workflow(name: str, graph: dict, execution_flow: list) -> Workflow:
        """Add a new workflow."""
        with Session(engine) as session:
            workflow = Workflow(
                workflow_name=name,
                graph_json=graph,
                execution_flow=execution_flow,
            )

            session.add(workflow)
            session.commit()
            session.refresh(workflow)

            return workflow

    @staticmethod
    def delete_workflow(workflow_id: str) -> bool:
        """Delete the workflow with the given ID."""
        with Session(engine) as session:
            workflow = session.get(Workflow, workflow_id)

            if workflow is None:
                return False

            session.delete(workflow)
            session.commit()

            return True

    @staticmethod
    def get_workflow(workflow_id: str) -> Workflow | None:
        """Return the workflow with the given ID."""
        with Session(engine) as session:
            return session.get(Workflow, workflow_id)

    @staticmethod
    def get_all() -> list[Workflow]:
        """Return all workflows."""
        with Session(engine) as session:
            statement = select(Workflow).order_by(Workflow.updated_at.desc())
            return list(session.scalars(statement).all())


class DbHandlerExecution:
    """Database handler for executions."""

    @staticmethod
    def insert_execution(workflow_id: str) -> Execution:
        """Add a new execution for the given workflow."""
        with Session(engine) as session:
            execution = Execution(
                workflow_id=workflow_id,
                current_state="PENDING",
            )

            session.add(execution)
            session.commit()
            session.refresh(execution)

            return execution

    @staticmethod
    def get_execution(reference_id: str) -> Execution | None:
        """Return the execution with the given ID."""
        with Session(engine) as session:
            return session.get(Execution, reference_id)

    @staticmethod
    def get_executions_by_workflow_id(workflow_id: str) -> list[Execution]:
        """Return all executions for the given workflow."""
        with Session(engine) as session:
            statement = (
                select(Execution)
                .where(Execution.workflow_id == workflow_id)
                .order_by(Execution.start_at.desc().nulls_last())
            )
            return list(session.scalars(statement).all())

    @staticmethod
    def get_all_executions() -> list[Execution]:
        """Return all executions."""
        with Session(engine) as session:
            statement = select(Execution).order_by(
                Execution.start_at.desc().nulls_last()
            )
            return list(session.scalars(statement).all())

    @staticmethod
    def get_executions_by_status(current_state: str) -> list[Execution]:
        """Return all executions with the given state."""
        with Session(engine) as session:
            statement = (
                select(Execution)
                .where(Execution.current_state == current_state)
                .order_by(Execution.start_at.desc().nulls_last())
            )
            return list(session.scalars(statement).all())

    @staticmethod
    def execution_started(reference_id: str) -> bool:
        """Start the execution with the given ID."""
        with Session(engine) as session:
            execution = session.get(Execution, reference_id)

            if execution is None:
                return False

            execution.start()
            session.commit()

            return True

    @staticmethod
    def execution_cancelled(reference_id: str) -> bool:
        """Cancel the execution with the given ID."""
        with Session(engine) as session:
            execution = session.get(Execution, reference_id)

            if execution is None:
                return False

            execution.cancel()
            session.commit()

            return True

    @staticmethod
    def execution_failed(reference_id: str) -> bool:
        """Fail the execution with the given ID."""
        with Session(engine) as session:
            execution = session.get(Execution, reference_id)

            if execution is None:
                return False

            execution.fail()
            session.commit()

            return True

    @staticmethod
    def execution_finished(reference_id: str) -> bool:
        """Finish the execution with the given ID."""
        with Session(engine) as session:
            execution = session.get(Execution, reference_id)

            if execution is None:
                return False

            execution.finish()
            session.commit()

            return True

    @staticmethod
    def reset() -> None:
        """Delete the execution table."""
        with Session(engine) as session:
            session.execute(delete(Execution))
            session.commit()
