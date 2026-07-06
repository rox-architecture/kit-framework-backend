from sqlalchemy import DDL, event

from cee.models.db.base import Base
from cee.models.db.execution import Execution
from cee.models.db.workflow import Workflow


event.listen(
    Base.metadata,
    "before_create",
    DDL("CREATE EXTENSION IF NOT EXISTS pgcrypto"),
)

event.listen(
    Base.metadata,
    "before_create",
    DDL(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    ),
)

event.listen(
    Workflow.__table__,
    "after_create",
    DDL(
        """
        CREATE TRIGGER trigger_set_updated_at
        BEFORE UPDATE ON workflows
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
        """
    ),
)

__all__ = ["Base", "Execution", "Workflow"]
