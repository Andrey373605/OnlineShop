from abc import ABC, abstractmethod

from shop.app.models.schemas import CartItemOut


class CartItemRepository(ABC):
    """Legacy SQL port for cart line items (until cart aggregate mapper exists)."""

    @abstractmethod
    async def get_by_cart_id(self, cart_id: int) -> list[CartItemOut]:
        """List line items for a cart."""

    @abstractmethod
    async def get_by_id(self, item_id: int) -> CartItemOut | None:
        """Fetch one cart line by id."""

    @abstractmethod
    async def get_by_cart_and_product(
        self, cart_id: int, product_id: int
    ) -> CartItemOut | None:
        """Find the line for a product within a cart."""

    @abstractmethod
    async def create(self, data: dict) -> int:
        """Insert a cart line; return new id."""

    @abstractmethod
    async def update(self, item_id: int, data: dict) -> bool:
        """Patch quantity or references; return True if updated."""

    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Remove a single line; return True if deleted."""

    @abstractmethod
    async def delete_by_cart_id(self, cart_id: int) -> list[int]:
        """Clear all lines for a cart; return removed ids."""
