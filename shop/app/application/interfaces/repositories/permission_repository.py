from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.permission import Permission


class PermissionRepository(ABC):
    """Persistence port for fine-grained permissions (master data)."""

    @abstractmethod
    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        """Load a permission by id."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Permission | None:
        """Load a permission by unique name."""

    @abstractmethod
    async def list_all(self) -> list[Permission]:
        """Return all permissions."""

    @abstractmethod
    async def add(self, permission: Permission) -> None:
        """Insert a permission."""

    @abstractmethod
    async def update(self, permission: Permission) -> None:
        """Persist name or other mutable fields."""

    @abstractmethod
    async def delete(self, permission_id: UUID) -> None:
        """Remove a permission by id."""
