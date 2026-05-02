from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.product_image import ProductImage


class ProductImageRepository(ABC):
    """Persistence port for product image metadata."""

    @abstractmethod
    async def get_by_id(self, image_id: UUID) -> ProductImage | None:
        """Load one image by id."""

    @abstractmethod
    async def list_by_product_id(self, product_id: UUID) -> list[ProductImage]:
        """List images attached to a product."""

    @abstractmethod
    async def add(self, image: ProductImage) -> None:
        """Insert image metadata."""

    @abstractmethod
    async def update(self, image: ProductImage) -> None:
        """Persist changes to an image row."""

    @abstractmethod
    async def delete(self, image_id: UUID) -> None:
        """Remove one image by id."""

    @abstractmethod
    async def delete_all_for_product(self, product_id: UUID) -> list[UUID]:
        """Remove all images for a product; return deleted image ids."""
