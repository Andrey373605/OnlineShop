from abc import ABC, abstractmethod


class AuthAttemptStoragePort(ABC):
    @abstractmethod
    async def get_failed_attempts(self, username: str) -> int: ...

    @abstractmethod
    async def increment_failed_attempts(self, username: str, window_seconds: int) -> int: ...

    @abstractmethod
    async def reset_failed_attempts(self, username: str) -> None: ...

    @abstractmethod
    async def add_to_blocklist(self, username: str, duration_seconds: int) -> None: ...

    @abstractmethod
    async def is_blacklisted(self, username: str) -> bool: ...
