from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OrderResponse:
    """Single-entity response DTO for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ListOrdersResponse:
    """List response DTO for application layer."""

    items: list[OrderResponse] = field(default_factory=list)
    total: int = 0


__all__ = [
    "OrderResponse",
    "ListOrdersResponse",
]
