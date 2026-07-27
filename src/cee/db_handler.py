from datetime import UTC, datetime
from typing import Any

from sqlalchemy import create_engine, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from cee.config import DATABASE_URL
from cee.models.db import Base, Execution, NodeExecution, Workflow

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)


def initialize_database() -> None:
    """Create tables that do not yet exist."""
    Base.metadata.create_all(engine)


class DbHandlerWorkflow:
    """Database handler for workflows."""

    @staticmethod
    def insert_workflow(
        name: str, graph: dict[str, Any], execution_flow: dict[str, Any]
    ) -> Workflow:
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
    def claim_pending() -> list[str]:
        """Atomically claim all pending executions and return their IDs."""
        with Session(engine) as session:
            pending = list(
                session.scalars(
                    select(Execution)
                    .where(Execution.current_state == "PENDING")
                    .with_for_update(skip_locked=True)
                ).all()
            )
            now = datetime.now(UTC)
            for execution in pending:
                execution.current_state = "RUNNING"
                execution.start_at = now
            session.commit()
            return [str(execution.reference_id) for execution in pending]

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

            if execution is None or execution.current_state in {
                "CANCELLED",
                "FAILED",
                "FINISHED",
            }:
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
    def current_state(reference_id: str) -> str | None:
        """Return the current state of an execution."""
        with Session(engine) as session:
            execution = session.get(Execution, reference_id)
            return execution.current_state if execution else None


class DbHandlerNodeExecution:
    """Database operations for node-level execution state."""

    @staticmethod
    def initialize(execution_id: str, node_ids: list[str]) -> None:
        """Create missing node-state rows for an execution."""
        with Session(engine) as session:
            existing = set(
                session.scalars(
                    select(NodeExecution.node_id).where(
                        NodeExecution.execution_id == execution_id
                    )
                ).all()
            )
            session.add_all(
                NodeExecution(execution_id=execution_id, node_id=node_id)
                for node_id in node_ids
                if node_id not in existing
            )
            session.commit()

    @staticmethod
    def get_all(execution_id: str) -> list[NodeExecution]:
        """Return all node-state rows for an execution."""
        with Session(engine) as session:
            statement = select(NodeExecution).where(
                NodeExecution.execution_id == execution_id
            )
            return list(session.scalars(statement).all())

    @staticmethod
    def queue(execution_id: str, node_id: str, task_id: str) -> bool:
        """Atomically move a pending node into the queue."""
        with Session(engine) as session:
            result = session.execute(
                update(NodeExecution)
                .where(
                    NodeExecution.execution_id == execution_id,
                    NodeExecution.node_id == node_id,
                    NodeExecution.current_state == "PENDING",
                )
                .values(
                    current_state="QUEUED",
                    celery_task_id=task_id,
                    queued_at=datetime.now(UTC),
                )
            )
            session.commit()
            return isinstance(result, CursorResult) and result.rowcount == 1

    @staticmethod
    def start(execution_id: str, node_id: str) -> bool:
        """Mark a queued node as running."""
        return DbHandlerNodeExecution._transition(
            execution_id, node_id, {"QUEUED"}, "RUNNING", start_at=datetime.now(UTC)
        )

    @staticmethod
    def finish(execution_id: str, node_id: str) -> bool:
        """Mark a running node as finished."""
        return DbHandlerNodeExecution._transition(
            execution_id,
            node_id,
            {"RUNNING"},
            "FINISHED",
            finish_at=datetime.now(UTC),
        )

    @staticmethod
    def fail(execution_id: str, node_id: str, error: str) -> bool:
        """Mark queued or running node work as failed."""
        return DbHandlerNodeExecution._transition(
            execution_id,
            node_id,
            {"QUEUED", "RUNNING"},
            "FAILED",
            finish_at=datetime.now(UTC),
            error_message=error[:8000],
        )

    @staticmethod
    def cancel_unfinished(execution_id: str) -> None:
        """Cancel nodes which have not begun running."""
        with Session(engine) as session:
            session.execute(
                update(NodeExecution)
                .where(
                    NodeExecution.execution_id == execution_id,
                    NodeExecution.current_state.in_({"PENDING", "QUEUED", "RUNNING"}),
                )
                .values(current_state="CANCELLED", finish_at=datetime.now(UTC))
            )
            session.commit()

    @staticmethod
    def _transition(
        execution_id: str,
        node_id: str,
        from_states: set[str],
        to_state: str,
        **values: object,
    ) -> bool:
        with Session(engine) as session:
            result = session.execute(
                update(NodeExecution)
                .where(
                    NodeExecution.execution_id == execution_id,
                    NodeExecution.node_id == node_id,
                    NodeExecution.current_state.in_(from_states),
                )
                .values(current_state=to_state, **values)
            )
            session.commit()
            return isinstance(result, CursorResult) and result.rowcount == 1
