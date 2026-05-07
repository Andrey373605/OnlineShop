from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import EmptyPermissionNameError


def _normalize_permission_name(name: str) -> str:
    if not isinstance(name, str):
        raise EmptyPermissionNameError("Permission name must be a string")
    clean = name.strip()
    if not clean:
        raise EmptyPermissionNameError("Permission name is required")
    return clean


class Permission:
    def __init__(self, id: UUID, name: str):
        self._id = id
        self._name = _normalize_permission_name(name)

    @classmethod
    def create(cls, name: str) -> "Permission":
        return cls(id=uuid7(), name=name)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"<Permission {self._name} ({self._id})>"
