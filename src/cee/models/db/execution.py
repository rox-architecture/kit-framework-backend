import uuid
from datetime import datetime, UTC

from sqlalchemy import text, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from cee.models.db.base import Base


class Execution(Base):
    """Model for executions."""

    __tablename__ = "executions"

    reference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    workflow_id: Mapped[str] = mapped_column(nullable=False)
    start_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finish_at: Mapped[datetime | None] = mapped_column(nullable=True)
    executed_nodes: Mapped[list[str]] = mapped_column(
        ARRAY(String()),
        nullable=False,
        server_default=text("'{}'")
    )
    current_state: Mapped[str] = mapped_column(nullable=False)

    def start(self) -> None:
        """Start the execution."""
        self.current_state = "RUNNING"
        self.start_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancel the execution."""
        self.current_state = "CANCELLED"
        self.finish_at = datetime.now(UTC)

    def fail(self) -> None:
        """Fail the execution."""
        self.current_state = "FAILED"
        self.finish_at = datetime.now(UTC)

    def finish(self) -> None:
        """Finish the execution."""
        self.current_state = "FINISHED"
        self.finish_at = datetime.now(UTC)
