from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateOrderCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteOrderCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetOrderByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListOrdersCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PlaceOrderCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CancelOrderCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ChangeOrderStatusCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateOrderCommand",
    "UpdateOrderCommand",
    "DeleteOrderCommand",
    "GetOrderByIdCommand",
    "ListOrdersCommand",
    "PlaceOrderCommand",
    "CancelOrderCommand",
    "ChangeOrderStatusCommand",
]
