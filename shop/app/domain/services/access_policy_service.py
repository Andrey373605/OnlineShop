
from collections.abc import Sequence

from shop.app.domain import Permission, Role, User


class AccessPolicyDomainService:
    """Resolves authorization rules from user roles and permissions."""

    def collect_effective_permissions(
        self,
        user: User,
        roles: Sequence[Role],
    ) -> set[str]:
        """Return effective permission codes for the user."""
        raise NotImplementedError("Domain service is not implemented yet")

    def ensure_permissions(
        self,
        user: User,
        roles: Sequence[Role],
        required_permissions: Sequence[Permission],
    ) -> None:
        """Validate that user has all required permissions."""
        raise NotImplementedError("Domain service is not implemented yet")


__all__ = ["AccessPolicyDomainService"]

