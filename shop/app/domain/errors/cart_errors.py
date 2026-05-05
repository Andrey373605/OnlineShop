
from shop.app.domain.errors.base import DomainError


class CartItemOwnershipError(DomainError):
    pass


class CartCurrencyMismatchError(DomainError):
    pass


class CartLineNotFoundError(DomainError):
    pass


class CartLinePriceMismatchError(DomainError):
    pass
