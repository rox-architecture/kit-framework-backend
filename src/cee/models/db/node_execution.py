"""Per-node execution state."""

from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from cee.models.db.base import Base


class NodeExecution(Base):
    """Persistent state for one node in one workflow execution."""

    __tablename__ = "node_executions"

    execution_id: Mapped[str] = mapped_column(String, primary_key=True)
    node_id: Mapped[str] = mapped_column(String, primary_key=True)
    current_state: Mapped[str] = mapped_column(
        String, nullable=False, default="PENDING"
    )
    celery_task_id: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queued_at: Mapped[datetime | None] = mapped_column(nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finish_at: Mapped[datetime | None] = mapped_column(nullable=True)
