from abc import ABC, abstractmethod
from pydantic import BaseModel

# This is an interface class to establish standardised interface for every adapter
# In this way, the connectors from different dataspace can be used in the same way
# It will allow us to switch between connectors, to do the conceptually same task
class Adapter(ABC):
    ...
