from abc import ABC, abstractmethod


class SessionStoragePort(ABC):
    @abstractmethod
    async def set(self, user_id: int, user_data: str) -> None: ...

    @abstractmethod
    async def get(self, user_id: int) -> str | None: ...

    @abstractmethod
    async def delete(self, user_id: int) -> None: ...
