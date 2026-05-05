
from typing import cast

from shop.app.domain.errors import DomainValidationError


class OrderNumber(str):
    def __new__(cls, value: str) -> OrderNumber:
        if not isinstance(value, str):
            raise DomainValidationError("Order number must be a string")
        clean = value.strip()
        if not clean:
            raise DomainValidationError("Order number cannot be empty")
        return cast(OrderNumber, str.__new__(cls, clean))


class ShippingAddress(str):
    def __new__(cls, value: str) -> ShippingAddress:
        if not isinstance(value, str):
            raise DomainValidationError("Shipping address must be a string")
        clean = value.strip()
        if not clean:
            raise DomainValidationError("Shipping address cannot be empty")
        return cast(ShippingAddress, str.__new__(cls, clean))


class PaymentMethod(str):
    def __new__(cls, value: str) -> PaymentMethod:
        if not isinstance(value, str):
            raise DomainValidationError("Payment method must be a string")
        clean = value.strip()
        if not clean:
            raise DomainValidationError("Payment method cannot be empty")
        return cast(PaymentMethod, str.__new__(cls, clean))


__all__ = [
    "OrderNumber",
    "ShippingAddress",
    "PaymentMethod",
]
