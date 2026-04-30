from abc import ABC, abstractmethod
from typing import Any


class ClientProviderPort(ABC):
    @abstractmethod
    def get_client(self) -> Any: ...
