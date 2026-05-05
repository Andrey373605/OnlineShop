from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain import Brand


class BrandRepository(ABC):
    """Persistence port for brands."""

    @abstractmethod
    async def get_by_id(self, brand_id: UUID) -> Brand | None:
        """Load a brand by id."""

    @abstractmethod
    async def list_all(self) -> list[Brand]:
        """Return all brands."""

    @abstractmethod
    async def add(self, brand: Brand) -> None:
        """Insert a new brand."""

    @abstractmethod
    async def update(self, brand: Brand) -> None:
        """Persist changes to an existing brand."""

    @abstractmethod
    async def delete(self, brand_id: UUID) -> None:
        """Remove a brand by id."""
