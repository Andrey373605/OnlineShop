
from shop.app.domain.errors.base import DomainError


class EmptySkuError(DomainError):
    """Raised when SKU is empty."""


class EmptyStorageKeyError(DomainError):
    """Raised when storage key is empty."""


class CurrencyMismatchError(DomainError):
    """Raised when aggregation includes mixed currencies."""
