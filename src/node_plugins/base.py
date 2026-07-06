from abc import ABC, abstractmethod
from pydantic import BaseModel
from schema.execution_schema import Item


class Base(ABC):

    # Input is always a list of Items
    class InputSpec(BaseModel):
        pass

    # Output is always a list of Items
    class OutputSpec(BaseModel):
        pass

    class ParamSpec(BaseModel):
        pass

    def __init__(self, node: dict):
        self.node = node
        self.node_id = node['id']
        self.params = {}
        self.outputs = {}
        self.finished = False

        # extract parameters from the node JSON 
        parameters_dict = self.node['data']['params']

        # check the required params and trim the other keys
        self.params = self.ParamSpec(**parameters_dict).model_dump()

        print(f'Node Object type {parameters_dict['type']} created for node_id ({self.node_id})')


    @classmethod
    def get_input_spec(cls):
        return cls.InputSpec.model_fields
    
    @classmethod
    def get_output_spec(cls):
        return cls.OutputSpec.model_fields
    
    @classmethod
    def get_param_spec(cls):
        return cls.ParamSpec.model_fields

    def set_output(self, port: int, item: Item) -> None:
        reference = f'output_{port}'
        self.outputs[reference] = item

    def get_output(self, ref: str) -> dict: 
        # check whether the output match the spec
        self.OutputSpec(**self.outputs)

        # Note: triggering get_output before 'run' can throw an error because the outputs are not yet created
        return self.outputs[ref]

    @abstractmethod
    def run(self, input_data: dict | None = None) -> None: 
        # input_data must match InputSpec
        # params must match ParamSpec
        # e.g., spec = self.InputSpec(**(input_spec or {}))
        ...