from abc import ABC, abstractmethod


class CacheStoragePort(ABC):
    @abstractmethod
    async def set_value(
        self, key: str, value: str | bytes, ttl_seconds: int | None = None
    ) -> None: ...

    @abstractmethod
    async def get_value(self, key: str) -> str | bytes | None: ...

    @abstractmethod
    async def delete_value(self, key: str) -> None: ...

    @abstractmethod
    async def delete_value_by_pattern(self, pattern: str) -> None: ...

    @abstractmethod
    async def exists_value(self, key: str) -> bool: ...
