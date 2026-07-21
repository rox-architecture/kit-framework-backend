from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field


class RequirementCategory(StrEnum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NEGOTIATION = "negotiation"


class Requirement(BaseModel):
    category: RequirementCategory
    key: str
    operator: Literal[
        "exists",
        "equals",
        "not_equals",
        "in",
        "min",
        "max",
        "compatible_with",
    ] = "exists"
    value: Any = True

    source_node_id: str | None = None
    source_node_type: str | None = None
    description: str | None = None

    # 같은 key의 requirement를 병합할 때 사용
    mandatory: bool = True