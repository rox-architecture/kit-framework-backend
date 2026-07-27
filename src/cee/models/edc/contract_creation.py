from typing import Any, Literal

from pydantic import Field

from cee.models.edc.entity import Entity, JsonLdEntity


class AssetsSelector(Entity):
    """EDC assets selector model."""

    at_type: Literal["Criterion"] = Field("Criterion", alias="@type")
    operand_left: Any
    operator: Any
    operand_right: Any


class ContractCreation(JsonLdEntity):
    """EDC contract creation model."""

    at_type: Literal["ContractDefinition"] = Field("ContractDefinition", alias="@type")
    access_policy_id: str
    contract_policy_id: str
    assets_selector: AssetsSelector
