from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.role import Role


class RoleRepository(ABC):
    """Persistence port for roles and their permission sets."""

    @abstractmethod
    async def get_by_id(self, role_id: UUID) -> Role | None:
        """Load a role with hydrated permissions."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        """Load a role by unique name."""

    @abstractmethod
    async def list_all(self) -> list[Role]:
        """Return all roles."""

    @abstractmethod
    async def add(self, role: Role) -> None:
        """Insert a role and its permission links."""

    @abstractmethod
    async def update(self, role: Role) -> None:
        """Persist role name and permission membership."""

    @abstractmethod
    async def delete(self, role_id: UUID) -> None:
        """Remove a role by id."""
