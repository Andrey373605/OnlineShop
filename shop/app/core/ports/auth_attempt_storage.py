from abc import ABC, abstractmethod


class AuthAttemptStoragePort(ABC):
    @abstractmethod
    async def get_attempts(self, username: str) -> int: ...

    @abstractmethod
    async def increment_attempts(self, username: str, window_seconds: int) -> int: ...

    @abstractmethod
    async def reset_attempts(self, username: str) -> None: ...

    @abstractmethod
    async def add_to_blocklist(
        self, username: str, duration_seconds: int, reason: str | None = None
    ) -> None: ...

    @abstractmethod
    async def is_blacklisted(self, username: str) -> bool: ...
