from pydantic import BaseModel
from schema.execution_schema import Item
from src.node_plugins.base import Base

class SaveToFile(Base):
    
    # Predefined Output specification
    class InputSpec(BaseModel):
        data: Item

    class ParamSpec(BaseModel):
        pass

    def __init__(self, node: dict):
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None: 
        print ("SaveToFile object triggered")