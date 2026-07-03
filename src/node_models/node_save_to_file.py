from pydantic import BaseModel


class SaveToFile():
    # Parameter specification
    class ParamSpec(BaseModel):
        name: str
    
    # Input specification (Array of "type:item")
    class InputSpec(BaseModel):
        pass

    # Output specification (Array of "type:item")
    class OutputSpec(BaseModel):
        pass

    def __init__(self, param: ParamSpec):
        pass

    def run(self, ):
        pass