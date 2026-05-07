from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.product_details import ProductDetails


class ProductDetailsRepository(ABC):
    """Persistence port for product-level attribute bag (1:1 with product)."""

    @abstractmethod
    async def get_by_id(self, details_id: UUID) -> ProductDetails | None:
        """Load details row by its id."""

    @abstractmethod
    async def get_by_product_id(self, product_id: UUID) -> ProductDetails | None:
        """Load details for a product, if present."""

    @abstractmethod
    async def add(self, details: ProductDetails) -> None:
        """Insert product details."""

    @abstractmethod
    async def update(self, details: ProductDetails) -> None:
        """Persist changes to product details."""

    @abstractmethod
    async def delete(self, details_id: UUID) -> None:
        """Remove a details row by id."""
