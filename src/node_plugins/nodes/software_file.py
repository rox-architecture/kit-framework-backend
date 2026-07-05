from pydantic import BaseModel
from schema.execution_schema import Item
from src.node_plugins.base import Base

class SoftwareFile(Base):
    
    # Predefined Output specification
    class OutputSpec(BaseModel):
        data: Item

    def __init__(self, node: dict):
        super().__init__(node)

    def run(self, input_data: dict | None = None) -> None: 
        print ("SoftwareFile object triggered")