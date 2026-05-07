from typing import Set
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.entities.permission import Permission
from shop.app.domain.errors import DomainValidationError, EmptyRoleNameError


def _normalize_role_name(name: str) -> str:
    if not isinstance(name, str):
        raise EmptyRoleNameError("Role name must be a string")
    clean = name.strip()
    if not clean:
        raise EmptyRoleNameError("Role name cannot be empty")
    return clean


class Role:
    def __init__(self, id: UUID, name: str, permissions: Set[Permission] | None = None):
        self._id = id
        self._name = _normalize_role_name(name)
        self._permissions: Set[Permission] = set(permissions) if permissions else set()
        if not all(isinstance(permission, Permission) for permission in self._permissions):
            raise DomainValidationError("Role permissions must contain Permission instances only")

    @classmethod
    def create(cls, name: str, permissions: Set[Permission]) -> "Role":
        return cls(id=uuid7(), name=name, permissions=permissions)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def permissions(self) -> frozenset[Permission]:
        return frozenset(self._permissions)

    def grant_permission(self, permission: Permission) -> None:
        if not isinstance(permission, Permission):
            raise DomainValidationError("Granted object must be Permission")
        self._permissions.add(permission)

    def revoke_permission(self, permission_id: UUID) -> None:
        self._permissions = {p for p in self._permissions if p.id != permission_id}

    def has_permission(self, name: str) -> bool:
        return any(p.name == name for p in self._permissions)

    def __repr__(self) -> str:
        return f"<Role {self._name} ({self._id})>"
