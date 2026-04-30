from abc import ABC, abstractmethod


class LifecyclePort(ABC):
    """Interface for managing the storage infrastructure lifecycle."""

    @abstractmethod
    async def connect(self) -> None:
        """Create connection with the storage"""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close connection with the storage"""
        ...


class HealthCheckPort(ABC):
    @abstractmethod
    async def ensure_ready(self) -> None:
        """Verify that storage is reachable and ready for operations."""
        ...
