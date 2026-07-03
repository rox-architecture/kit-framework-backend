from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID
from typing import Any, Literal


class GraphInput(BaseModel):
    workflow_name: str
    graph_json: dict[str, Any] = Field(default_factory=dict)


class ExecRequestInput(BaseModel):
    workflow_id: str