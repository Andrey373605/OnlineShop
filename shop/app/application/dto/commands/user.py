from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteUserCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetUserByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListUsersCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AssignRoleToUserCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RevokeRoleFromUserCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateUserCommand",
    "UpdateUserCommand",
    "DeleteUserCommand",
    "GetUserByIdCommand",
    "ListUsersCommand",
    "AssignRoleToUserCommand",
    "RevokeRoleFromUserCommand",
]
