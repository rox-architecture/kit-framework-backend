from pydantic import BaseModel
from schema.execution_schema import Item
from src.node_plugins.base import Base

class ServiceStream(Base):
    
    # Predefined Input specification
    class InputSpec(BaseModel):
        pass

    # Predefined Output specification
    class OutputSpec(BaseModel):
        data: Item

    def __init__(self, node: dict):
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None: 
        print ("ServiceStream object triggered")