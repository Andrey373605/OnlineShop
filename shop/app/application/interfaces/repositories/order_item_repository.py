from abc import ABC, abstractmethod

from shop.app.models.schemas import OrderItemOut


class OrderItemRepository(ABC):
    """Legacy SQL port for order line items (until order aggregate mapper exists)."""

    @abstractmethod
    async def get_by_order_id(self, order_id: int) -> list[OrderItemOut]:
        """List all lines belonging to an order."""

    @abstractmethod
    async def get_by_id(self, item_id: int) -> OrderItemOut | None:
        """Fetch a single order line."""

    @abstractmethod
    async def create(self, data: dict) -> int:
        """Insert a line; return new id."""

    @abstractmethod
    async def update(self, item_id: int, data: dict) -> bool:
        """Patch line fields; return True if updated."""

    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Remove one line; return True if deleted."""

    @abstractmethod
    async def delete_by_order_id(self, order_id: int) -> list[int]:
        """Remove every line for an order; return deleted ids."""
