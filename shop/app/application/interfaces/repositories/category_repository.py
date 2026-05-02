from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain import Category


class CategoryRepository(ABC):
    """Persistence port for product categories."""

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None:
        """Load a category by id."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Category | None:
        """Load a category by unique name."""

    @abstractmethod
    async def list_all(self) -> list[Category]:
        """Return all categories."""

    @abstractmethod
    async def add(self, category: Category) -> None:
        """Insert a new category."""

    @abstractmethod
    async def update(self, category: Category) -> None:
        """Persist changes to an existing category."""

    @abstractmethod
    async def delete(self, category_id: UUID) -> None:
        """Remove a category by id."""

    @abstractmethod
    async def exists_with_name(self, name: str, *, exclude_id: UUID | None = None) -> bool:
        """Return True if name is taken, optionally ignoring one id (for updates)."""
