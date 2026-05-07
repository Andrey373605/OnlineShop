from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProductResponse:
    """Single-entity response DTO for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ListProductsResponse:
    """List response DTO for application layer."""

    items: list[ProductResponse] = field(default_factory=list)
    total: int = 0


__all__ = [
    "ProductResponse",
    "ListProductsResponse",
]
