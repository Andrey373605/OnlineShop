from abc import ABC, abstractmethod
from typing import Any


class PoolProvider(ABC):
    @abstractmethod
    def get_pool(self) -> Any: ...


class ClientProvider(ABC):
    @abstractmethod
    def get_client(self) -> Any: ...
