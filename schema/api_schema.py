from pydantic import BaseModel, Field
from typing import Any

class GraphInput(BaseModel):
    workflow_name: str
    graph_json: dict[str, Any] = Field(default_factory=dict)

class ExecRequestInput(BaseModel):
    workflow_id: str