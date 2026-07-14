from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel
from cee.schema.execution_schema import Item


class Base(ABC):
    """Base class for nodes."""

    # Input is always a list of Items
    class InputSpec(BaseModel):
        """Base input spec."""

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        """Base output spec."""

    class ParamSpec(BaseModel):
        """Base param spec."""

    def __init__(self, node: dict[str, Any]) -> None:
        """Initialize the instance."""
        self.node = node
        self.node_id = node["id"]
        self.params = {}
        self.outputs = {}
        self.finished = False

        # extract parameters from the node JSON
        parameters_dict = self.node["data"]["params"]

        # check the required params and trim the other keys
        self.params = self.ParamSpec(**parameters_dict).model_dump()

        print(f'Node Object type {parameters_dict['type']} created for node_id ({self.node_id})')

    @classmethod
    def get_input_spec(cls):
        """Return the input spec."""
        return cls.InputSpec.model_fields

    @abstractmethod
    def check_validty(self) -> bool:
        # If nothing to check, return True by default
        ...

    @classmethod
    def get_output_spec(cls):
        """Return the output spec."""
        return cls.OutputSpec.model_fields

    @classmethod
    def get_param_spec(cls):
        """Return the param spec."""
        return cls.ParamSpec.model_fields

    def set_output(self, port: int, item: Item) -> None:
        reference = f'output_{port}'
        self.outputs[reference] = item

    def get_output(self, ref: str) -> dict: 
        # check whether the output match the spec
        self.OutputSpec(**self.outputs)

        # Note: triggering get_output before 'run' can throw an error because the outputs are not yet created
        return self.outputs.get(ref)

    @abstractmethod
    def run(self, input_data: dict | None = None) -> None:
        """Run the node."""
        # input_data must match InputSpec
        # params must match ParamSpec
        # e.g., spec = self.InputSpec(**(input_spec or {}))
        ...
