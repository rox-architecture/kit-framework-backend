from abc import ABC, abstractmethod
from pydantic import BaseModel

class Base(ABC):

    class InputSpec(BaseModel):
        pass

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

        print(f'Node Object "data_container" created for node_id ({self.node_id})')


    @classmethod
    def get_input_spec(cls):
        return cls.InputSpec.model_fields
    
    @classmethod
    def get_output_spec(cls):
        return cls.OutputSpec.model_fields
    
    @classmethod
    def get_param_spec(cls):
        return cls.ParamSpec.model_fields

    def get_output(self) -> dict: 
        # check whether the output match the spec
        self.OutputSpec(**self.outputs) 
        # Note: triggering get_output before 'run' can throw an error because the outputs are not yet created
        return self.outputs

    @abstractmethod
    def run(self, input_data: dict | None = None) -> None: 
        # input_data must match InputSpec
        # params must match ParamSpec
        # e.g., spec = self.InputSpec(**(input_spec or {}))
        ...