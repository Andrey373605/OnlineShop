from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.entities.cart.validators import validate_line_quantity, validate_max_stock
from shop.app.domain.value_objects.price import Price
from shop.app.domain.errors import NonPositiveQuantityError


class CartItem:
    """Cart line: product, quantity, and unit price snapshot."""

    def __init__(
        self,
        id: UUID,
        cart_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Price,
    ) -> None:
        validate_line_quantity(quantity)
        self._id = id
        self._cart_id = cart_id
        self._product_id = product_id
        self._quantity = quantity
        self._unit_price = unit_price

    @classmethod
    def create(
        cls,
        cart_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Price,
    ) -> "CartItem":
        return cls(
            id=uuid7(),
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def cart_id(self) -> UUID:
        return self._cart_id

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

    def change_quantity(self, new_quantity: int, *, max_stock: int | None = None) -> None:
        validate_line_quantity(new_quantity)
        validate_max_stock(new_quantity, max_stock)
        self._quantity = new_quantity

    def add_quantity(self, delta: int, *, max_stock: int | None = None) -> None:
        if delta < 1:
            raise NonPositiveQuantityError("Added quantity must be at least 1")
        self.change_quantity(self._quantity + delta, max_stock=max_stock)

    def __repr__(self) -> str:
        return f"<CartItem product={self._product_id} qty={self._quantity} ({self._id})>"
