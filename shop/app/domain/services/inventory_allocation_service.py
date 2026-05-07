
from collections.abc import Mapping
from uuid import UUID

from shop.app.domain import Cart, StockMovement, Warehouse


class InventoryAllocationDomainService:
    """Defines stock allocation rules across cart, movement, and warehouse."""

    def ensure_allocation_possible(
        self,
        cart: Cart,
        warehouse: Warehouse,
        on_hand_by_product_id: Mapping[UUID, int],
    ) -> None:
        """Validate that all cart items can be allocated from warehouse stock."""
        raise NotImplementedError("Domain service is not implemented yet")

    def plan_allocations(
        self,
        cart: Cart,
        warehouse: Warehouse,
        on_hand_by_product_id: Mapping[UUID, int],
    ) -> list[StockMovement]:
        """Build planned stock movements required for checkout allocation."""
        raise NotImplementedError("Domain service is not implemented yet")


__all__ = ["InventoryAllocationDomainService"]

