from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateStockMovementCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateStockMovementCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteStockMovementCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetStockMovementByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListStockMovementsCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReserveStockCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReleaseStockCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TransferStockCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateStockMovementCommand",
    "UpdateStockMovementCommand",
    "DeleteStockMovementCommand",
    "GetStockMovementByIdCommand",
    "ListStockMovementsCommand",
    "ReserveStockCommand",
    "ReleaseStockCommand",
    "TransferStockCommand",
]
