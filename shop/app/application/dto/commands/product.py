from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateProductCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateProductCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteProductCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetProductByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListProductsCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PublishProductCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ArchiveProductCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateProductCommand",
    "UpdateProductCommand",
    "DeleteProductCommand",
    "GetProductByIdCommand",
    "ListProductsCommand",
    "PublishProductCommand",
    "ArchiveProductCommand",
]
