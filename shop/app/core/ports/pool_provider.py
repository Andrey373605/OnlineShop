from abc import ABC, abstractmethod
from typing import Any


class PoolProviderPort(ABC):
    @abstractmethod
    def get_pool(self) -> Any: ...
