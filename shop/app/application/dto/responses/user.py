from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserResponse:
    """Single-entity response DTO for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ListUsersResponse:
    """List response DTO for application layer."""

    items: list[UserResponse] = field(default_factory=list)
    total: int = 0


__all__ = [
    "UserResponse",
    "ListUsersResponse",
]
