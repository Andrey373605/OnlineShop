
from shop.app.domain.errors.base import DomainError


class OrderCancellationNotAllowedError(DomainError):
    """Raised when order cancellation is forbidden by current status."""


class OrderShipmentNotAllowedError(DomainError):
    """Raised when order cannot be shipped from current state."""


class OrderDeliveryNotAllowedError(DomainError):
    """Raised when order cannot be marked as delivered from current state."""


class PaymentTransitionNotAllowedError(DomainError):
    """Raised when payment status transition is invalid."""


class OrderLineRequiredError(DomainError):
    """Raised when order creation is requested without line items."""


class OrderItemOwnershipError(DomainError):
    """Raised when an order item points to another order aggregate."""


class OrderHasNoLinesError(DomainError):
    """Raised when total is requested for an empty order."""
