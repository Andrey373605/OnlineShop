from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateReviewCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateReviewCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteReviewCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetReviewByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListReviewsCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateReviewCommand",
    "UpdateReviewCommand",
    "DeleteReviewCommand",
    "GetReviewByIdCommand",
    "ListReviewsCommand",
]
