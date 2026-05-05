"""Shopping cart aggregate root."""

from decimal import Decimal
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.entities.cart.cart_item import CartItem
from shop.app.domain.entities.cart.validators import validate_line_quantity, validate_max_stock
from shop.app.domain.value_objects.price import Price, quantize_money_amount
from shop.app.domain.errors import CartCurrencyMismatchError, CartItemOwnershipError, CartLineNotFoundError, CartLinePriceMismatchError


class Cart:
    """User cart aggregate root including line items."""

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        items: list[CartItem] | None = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._items: list[CartItem] = list(items) if items else []
        self._ensure_items_belong_to_cart()

    def _ensure_items_belong_to_cart(self) -> None:
        for item in self._items:
            if item.cart_id != self._id:
                raise CartItemOwnershipError("Cart item belongs to another cart")

    @classmethod
    def create(cls, user_id: UUID) -> "Cart":
        return cls(
            id=uuid7(),
            user_id=user_id,
            items=[],
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def items(self) -> tuple[CartItem, ...]:
        return tuple(self._items)

    @property
    def total_price(self) -> Price | None:
        if not self._items:
            return None
        currency = self._items[0].unit_price.currency
        acc = Decimal("0")
        for item in self._items:
            if item.unit_price.currency != currency:
                raise CartCurrencyMismatchError("Cart lines must share the same currency")
            acc += item.line_subtotal().amount
        return Price(quantize_money_amount(acc), currency)

    @property
    def total_amount(self) -> Decimal:
        tp = self.total_price
        return Decimal("0") if tp is None else tp.amount

    def line_by_product_id(self, product_id: UUID) -> CartItem | None:
        for item in self._items:
            if item.product_id == product_id:
                return item
        return None

    def add_product_line(
        self,
        product_id: UUID,
        quantity: int,
        unit_price: Price,
        *,
        max_stock: int | None = None,
    ) -> CartItem:
        validate_line_quantity(quantity)
        existing = self.line_by_product_id(product_id)
        if existing is not None:
            if existing.unit_price != unit_price:
                raise CartLinePriceMismatchError(
                    "Unit price does not match existing line for this product",
                )
            existing.add_quantity(quantity, max_stock=max_stock)
            return existing
        validate_max_stock(quantity, max_stock)
        line = CartItem.create(self._id, product_id, quantity, unit_price)
        self._items.append(line)
        return line

    def update_line_quantity(
        self,
        line_id: UUID,
        new_quantity: int,
        *,
        max_stock: int | None = None,
    ) -> None:
        self._line_by_id(line_id).change_quantity(new_quantity, max_stock=max_stock)

    def remove_line(self, line_id: UUID) -> None:
        before = len(self._items)
        self._items = [i for i in self._items if i.id != line_id]
        if len(self._items) == before:
            raise CartLineNotFoundError("Cart line not found")

    def clear(self) -> None:
        self._items.clear()

    def _line_by_id(self, line_id: UUID) -> CartItem:
        for item in self._items:
            if item.id == line_id:
                return item
        raise CartLineNotFoundError("Cart line not found")

    def __repr__(self) -> str:
        return f"<Cart user={self._user_id} lines={len(self._items)} ({self._id})>"
