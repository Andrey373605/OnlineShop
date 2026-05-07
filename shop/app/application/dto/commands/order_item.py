from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateOrderItemCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateOrderItemCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteOrderItemCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetOrderItemByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListOrderItemsCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateOrderItemCommand",
    "UpdateOrderItemCommand",
    "DeleteOrderItemCommand",
    "GetOrderItemByIdCommand",
    "ListOrderItemsCommand",
]
