from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.product_variant_details import ProductVariantDetails


class ProductVariantDetailsRepository(ABC):
    """Persistence port for variant-level attribute bag (1:1 with variant)."""

    @abstractmethod
    async def get_by_id(self, details_id: UUID) -> ProductVariantDetails | None:
        """Load details row by its id."""

    @abstractmethod
    async def get_by_variant_id(self, variant_id: UUID) -> ProductVariantDetails | None:
        """Load details for a variant, if present."""

    @abstractmethod
    async def add(self, details: ProductVariantDetails) -> None:
        """Insert variant details."""

    @abstractmethod
    async def update(self, details: ProductVariantDetails) -> None:
        """Persist changes to variant details."""

    @abstractmethod
    async def delete(self, details_id: UUID) -> None:
        """Remove a details row by id."""
