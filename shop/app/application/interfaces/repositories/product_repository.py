from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.product import Product


class ProductRepository(ABC):
    """Persistence port for catalog products (header row, not variants)."""

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Product | None:
        """Load a product by id."""

    @abstractmethod
    async def list_by_category(self, category_id: UUID) -> list[Product]:
        """List products in a category."""

    @abstractmethod
    async def list_published(self, limit: int, offset: int) -> list[Product]:
        """Page through published products for storefront listings."""

    @abstractmethod
    async def add(self, product: Product) -> None:
        """Insert a new product."""

    @abstractmethod
    async def update(self, product: Product) -> None:
        """Persist changes to an existing product."""

    @abstractmethod
    async def delete(self, product_id: UUID) -> None:
        """Remove a product by id."""
