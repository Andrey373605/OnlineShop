
from collections.abc import Mapping, Sequence
from decimal import Decimal
from uuid import UUID

from shop.app.domain import Cart, Order, Price, User


class DiscountPolicyDomainService:
    """Evaluates discount rules that depend on cart and user order history."""

    def calculate_discount_by_product(
        self,
        user: User,
        cart: Cart,
        user_orders: Sequence[Order],
        base_price_by_product_id: Mapping[UUID, Price],
    ) -> Mapping[UUID, Decimal]:
        """Return discount amount by product id."""
        raise NotImplementedError("Domain service is not implemented yet")

    def apply_discounts(
        self,
        base_price_by_product_id: Mapping[UUID, Price],
        discount_by_product_id: Mapping[UUID, Decimal],
    ) -> Mapping[UUID, Price]:
        """Return discounted prices by product id."""
        raise NotImplementedError("Domain service is not implemented yet")


__all__ = ["DiscountPolicyDomainService"]

