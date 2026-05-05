"""Order aggregate root."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import (
    CurrencyMismatchError,
    DomainValidationError,
    OrderCancellationNotAllowedError,
    OrderHasNoLinesError,
    OrderItemOwnershipError,
    OrderLineRequiredError,
    OrderDeliveryNotAllowedError,
    OrderShipmentNotAllowedError,
    PaymentTransitionNotAllowedError,
)
from shop.app.domain.enums.order_enums import OrderStatus, PaymentStatus
from shop.app.domain.entities.order.order_item import OrderItem
from shop.app.domain.value_objects.order_values import (
    OrderNumber,
    PaymentMethod,
    ShippingAddress,
)
from shop.app.domain.value_objects.price import Price, quantize_money_amount
from shop.app.utils.get_utc_now import get_utc_now


class Order:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        order_number: OrderNumber,
        status: OrderStatus,
        payment_status: PaymentStatus,
        shipping_address: ShippingAddress,
        payment_method: PaymentMethod,
        items: list[OrderItem],
        created_at: datetime | None = None,
    ) -> None:
        if not isinstance(id, UUID):
            raise DomainValidationError("Order id must be UUID")
        if not isinstance(user_id, UUID):
            raise DomainValidationError("Order user id must be UUID")
        if not isinstance(status, OrderStatus):
            raise DomainValidationError("Order status must be OrderStatus")
        if not isinstance(payment_status, PaymentStatus):
            raise DomainValidationError("Payment status must be PaymentStatus")
        self._id = id
        self._user_id = user_id
        self._order_number = order_number
        self._status = status
        self._payment_status = payment_status
        self._shipping_address = shipping_address
        self._payment_method = payment_method
        self._items: list[OrderItem] = list(items)
        if not self._items:
            raise OrderLineRequiredError("Order must contain at least one line")
        self._created_at = created_at or get_utc_now()
        self._ensure_items_belong_to_order()

    def _ensure_items_belong_to_order(self) -> None:
        for item in self._items:
            if item.order_id != self._id:
                raise OrderItemOwnershipError("Order item belongs to another order")

    @classmethod
    def place(
        cls,
        user_id: UUID,
        order_number: OrderNumber,
        shipping_address: ShippingAddress,
        payment_method: PaymentMethod,
        lines: list[tuple[UUID, int, Price]],
    ) -> "Order":
        if not lines:
            raise OrderLineRequiredError("Order must contain at least one line")
        order_id = uuid7()
        order_items = [
            OrderItem.create(order_id, product_id, quantity, unit_price)
            for product_id, quantity, unit_price in lines
        ]
        return cls(
            id=order_id,
            user_id=user_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            shipping_address=shipping_address,
            payment_method=payment_method,
            items=order_items,
            created_at=get_utc_now(),
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def order_number(self) -> OrderNumber:
        return self._order_number

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def payment_status(self) -> PaymentStatus:
        return self._payment_status

    @property
    def shipping_address(self) -> ShippingAddress:
        return self._shipping_address

    @property
    def payment_method(self) -> PaymentMethod:
        return self._payment_method

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)

    @property
    def total_price(self) -> Price:
        if not self._items:
            raise OrderHasNoLinesError("Order has no lines")
        currency = self._items[0].unit_price.currency
        acc = Decimal("0")
        for item in self._items:
            if item.unit_price.currency != currency:
                raise CurrencyMismatchError("Order lines must share the same currency")
            acc += item.line_subtotal().amount
        return Price(quantize_money_amount(acc), currency)

    def cancel(self) -> None:
        if self._status == OrderStatus.CANCELLED:
            return
        if self._status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise OrderCancellationNotAllowedError(
                "Cannot cancel order that is already shipped or delivered",
            )
        self._status = OrderStatus.CANCELLED

    def mark_paid(self) -> None:
        if self._status == OrderStatus.CANCELLED:
            raise PaymentTransitionNotAllowedError("Cannot mark cancelled order as paid")
        if self._payment_status == PaymentStatus.PAID:
            return
        if self._payment_status not in (PaymentStatus.PENDING, PaymentStatus.FAILED):
            raise PaymentTransitionNotAllowedError(
                "Payment cannot transition to paid from current state",
            )
        self._payment_status = PaymentStatus.PAID
        if self._status == OrderStatus.PENDING:
            self._status = OrderStatus.PROCESSING

    def mark_shipped(self) -> None:
        if self._status == OrderStatus.CANCELLED:
            raise OrderShipmentNotAllowedError("Cannot ship a cancelled order")
        if self._payment_status != PaymentStatus.PAID:
            raise OrderShipmentNotAllowedError("Cannot ship an unpaid order")
        if self._status == OrderStatus.SHIPPED:
            return
        if self._status != OrderStatus.PROCESSING:
            raise OrderShipmentNotAllowedError("Order must be processing before shipment")
        self._status = OrderStatus.SHIPPED

    def mark_delivered(self) -> None:
        if self._status == OrderStatus.CANCELLED:
            raise OrderDeliveryNotAllowedError("Cannot complete a cancelled order")
        if self._status == OrderStatus.DELIVERED:
            return
        if self._status != OrderStatus.SHIPPED:
            raise OrderDeliveryNotAllowedError("Order must be shipped before delivery")
        self._status = OrderStatus.DELIVERED

    def __repr__(self) -> str:
        return f"<Order {self._order_number!r} ({self._id})>"
