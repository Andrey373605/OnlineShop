from abc import ABC, abstractmethod

from shop.app.models.schemas import ProductSpecificationOut


class ProductSpecificationRepository(ABC):
    """Legacy SQL port for JSON product specifications (pre-domain ProductDetails)."""

    @abstractmethod
    async def get_all(self) -> list[ProductSpecificationOut]:
        """Load every specification row."""

    @abstractmethod
    async def get_by_id(self, specification_id: int) -> ProductSpecificationOut | None:
        """Fetch one specification by id."""

    @abstractmethod
    async def get_by_product_id(self, product_id: int) -> ProductSpecificationOut | None:
        """Fetch specification for a product id."""

    @abstractmethod
    async def create(self, data: dict) -> int:
        """Insert specifications; return new row id."""

    @abstractmethod
    async def update(self, specification_id: int, data: dict) -> bool:
        """Patch specification fields; return True if updated."""

    @abstractmethod
    async def delete(self, specification_id: int) -> bool:
        """Delete a specification row; return True if removed."""
