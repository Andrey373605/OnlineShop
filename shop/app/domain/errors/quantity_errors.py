
from shop.app.domain.errors.base import DomainError


class InvalidQuantityTypeError(DomainError):
    """Raised when quantity has invalid runtime type."""


class NonPositiveQuantityError(DomainError):
    """Raised when quantity must be strictly positive."""


class ExceedsAvailableStockError(DomainError):
    """Raised when requested quantity exceeds available stock."""

    def __init__(self, requested: int, available: int) -> None:
        self.requested = requested
        self.available = available
        super().__init__(
            f"Requested quantity {requested} exceeds available stock {available}",
        )
