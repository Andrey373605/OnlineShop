from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.product_variant import ProductVariant


class ProductVariantRepository(ABC):
    """Persistence port for purchasable SKUs / variants."""

    @abstractmethod
    async def get_by_id(self, variant_id: UUID) -> ProductVariant | None:
        """Load a variant by id."""

    @abstractmethod
    async def get_by_sku(self, sku: str) -> ProductVariant | None:
        """Load a variant by SKU."""

    @abstractmethod
    async def list_by_product_id(self, product_id: UUID) -> list[ProductVariant]:
        """List all variants for a product."""

    @abstractmethod
    async def add(self, variant: ProductVariant) -> None:
        """Insert a new variant."""

    @abstractmethod
    async def update(self, variant: ProductVariant) -> None:
        """Persist changes to an existing variant."""

    @abstractmethod
    async def delete(self, variant_id: UUID) -> None:
        """Remove a variant by id."""
