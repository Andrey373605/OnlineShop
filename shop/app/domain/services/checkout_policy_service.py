
from collections.abc import Mapping, Sequence
from uuid import UUID

from shop.app.domain import Cart, Order, User, Warehouse
from shop.app.domain.value_objects.order_values import OrderNumber, PaymentMethod, ShippingAddress


class CheckoutPolicyDomainService:
    """Coordinates checkout domain rules that span user, cart, and warehouse."""

    def ensure_checkout_allowed(
        self,
        user: User,
        cart: Cart,
        warehouse: Warehouse,
        user_orders: Sequence[Order],
        available_stock_by_product_id: Mapping[UUID, int],
    ) -> None:
        """Validate checkout constraints before creating an order."""
        raise NotImplementedError("Domain service is not implemented yet")

    def build_order_draft(
        self,
        user: User,
        cart: Cart,
        warehouse: Warehouse,
        order_number: OrderNumber,
        shipping_address: ShippingAddress,
        payment_method: PaymentMethod,
    ) -> Order:
        """Build an order draft from validated checkout input."""
        raise NotImplementedError("Domain service is not implemented yet")


__all__ = ["CheckoutPolicyDomainService"]

