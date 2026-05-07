from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.entities.cart import validate_line_quantity
from shop.app.domain.value_objects.price import Price


class OrderItem:
    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Price,
    ) -> None:
        validate_line_quantity(quantity)
        self._id = id
        self._order_id = order_id
        self._product_id = product_id
        self._quantity = quantity
        self._unit_price = unit_price

    @classmethod
    def create(
        cls,
        order_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Price,
    ) -> "OrderItem":
        return cls(
            id=uuid7(),
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def product_id(self) -> UUID:
        return self._product_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def unit_price(self) -> Price:
        return self._unit_price

    def line_subtotal(self) -> Price:
        return self._unit_price.times_quantity(self._quantity)

    def __repr__(self) -> str:
        return f"<OrderItem order={self._order_id} product={self._product_id} qty={self._quantity}>"
