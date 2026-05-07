
from shop.app.domain.errors.base import DomainError


class ZeroStockMovementAmountError(DomainError):
    pass


class InvalidSaleMovementAmountError(DomainError):
    pass


class InvalidReceiptMovementAmountError(DomainError):
    pass
