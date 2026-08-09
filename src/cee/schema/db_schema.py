from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class WorkflowCols(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workflow_id: UUID
    workflow_name: str
    updated_at: datetime
    graph_json: dict
    execution_flow: dict