from pydantic import BaseModel, Field
from typing import Any


class GraphInput(BaseModel):
    """Graph input model."""

    workflow_name: str
    graph_json: dict[str, Any] = Field(default_factory=dict)


class ExecRequestInput(BaseModel):
    """Execution request model."""

    workflow_id: str
