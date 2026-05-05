from datetime import datetime
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import (
    DomainValidationError,
    InvalidReceiptMovementAmountError,
    InvalidSaleMovementAmountError,
    ZeroStockMovementAmountError,
)
from shop.app.domain.enums.inventory_enums import MovementReason
from shop.app.utils.get_utc_now import get_utc_now


def _validate_movement(
    amount: int,
    reason: MovementReason,
) -> None:
    if not isinstance(amount, int) or isinstance(amount, bool):
        raise DomainValidationError("Movement amount must be an integer")
    if not isinstance(reason, MovementReason):
        raise DomainValidationError("Movement reason must be MovementReason")
    if amount == 0:
        raise ZeroStockMovementAmountError("Movement amount cannot be zero")
    if reason == MovementReason.SALE and amount > 0:
        raise InvalidSaleMovementAmountError("Sale stock movement amount must be negative")
    if reason == MovementReason.RECEIPT and amount < 0:
        raise InvalidReceiptMovementAmountError("Receipt stock movement amount must be positive")


class StockMovement:
    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        warehouse_id: UUID,
        amount: int,
        reason: MovementReason,
        created_at: datetime,
        product_variant_id: UUID | None = None,
    ) -> None:
        _validate_movement(amount, reason)
        self._id = id
        self._product_id = product_id
        self._warehouse_id = warehouse_id
        self._amount = amount
        self._reason = reason
        self._created_at = created_at
        self._product_variant_id = product_variant_id

    @classmethod
    def create(
        cls,
        product_id: UUID,
        warehouse_id: UUID,
        amount: int,
        reason: MovementReason,
        product_variant_id: UUID | None = None,
    ) -> "StockMovement":
        _validate_movement(amount, reason)
        return cls(
            id=uuid7(),
            product_id=product_id,
            warehouse_id=warehouse_id,
            amount=amount,
            reason=reason,
            created_at=get_utc_now(),
            product_variant_id=product_variant_id,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def product_id(self) -> UUID:
        return self._product_id

    @property
    def warehouse_id(self) -> UUID:
        return self._warehouse_id

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def reason(self) -> MovementReason:
        return self._reason

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def product_variant_id(self) -> UUID | None:
        return self._product_variant_id

    def __repr__(self) -> str:
        return f"<Stock Movement reason: {self._reason} amount: {self._amount}>"
