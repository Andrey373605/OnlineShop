from abc import ABC, abstractmethod


class CacheStoragePort(ABC):
    @abstractmethod
    async def set(self, key: str, value: str | bytes, ttl_seconds: int | None = None) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> str | bytes | None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def delete_pattern(self, key: str) -> None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...
