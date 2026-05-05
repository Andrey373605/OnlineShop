from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateRoleCommand:
    """Create request payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateRoleCommand:
    """Update request payload for application layer."""

    id: UUID
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class DeleteRoleCommand:
    """Delete request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class GetRoleByIdCommand:
    """Get-by-id request payload for application layer."""

    id: UUID


@dataclass(frozen=True, slots=True)
class ListRolesCommand:
    """List request payload for application layer."""

    limit: int = 50
    offset: int = 0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GrantPermissionToRoleCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RevokePermissionFromRoleCommand:
    """Domain-specific command payload for application layer."""

    data: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "CreateRoleCommand",
    "UpdateRoleCommand",
    "DeleteRoleCommand",
    "GetRoleByIdCommand",
    "ListRolesCommand",
    "GrantPermissionToRoleCommand",
    "RevokePermissionFromRoleCommand",
]
