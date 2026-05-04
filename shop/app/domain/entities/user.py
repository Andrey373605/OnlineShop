from datetime import datetime, UTC
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import DomainValidationError
from shop.app.domain.value_objects.user_values import Email, FullName, Username
from shop.app.utils.get_utc_now import get_utc_now


class User:
    def __init__(
        self,
        id: UUID,
        username: Username,
        email: Email,
        full_name: FullName,
        password_hash: str,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_login: datetime | None = None,
    ):
        if not isinstance(id, UUID):
            raise DomainValidationError("User id must be UUID")
        if not isinstance(username, Username):
            raise DomainValidationError("Username must be Username value object")
        if not isinstance(email, Email):
            raise DomainValidationError("Email must be Email value object")
        if not isinstance(full_name, FullName):
            raise DomainValidationError("Full name must be FullName value object")
        if not isinstance(password_hash, str) or not password_hash.strip():
            raise DomainValidationError("Password hash cannot be empty")
        self._id = id
        self._username = username
        self._email = email
        self._full_name = full_name
        self._password_hash = password_hash.strip()
        self._is_active = is_active

        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or self._created_at
        self._last_login = last_login

    @classmethod
    def create(
        cls,
        username: Username,
        email: Email,
        full_name: FullName,
        password_hash: str,
    ) -> "User":
        return cls(
            id=uuid7(),
            username=username,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def username(self) -> Username:
        return self._username

    @property
    def full_name(self) -> FullName:
        return self._full_name

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def is_active(self) -> bool:
        return self._is_active

    def change_email(self, new_email: Email) -> None:
        if self._email != new_email:
            self._email = new_email
            self._touch()

    def update_password(self, new_hash: str) -> None:
        if not isinstance(new_hash, str) or not new_hash.strip():
            raise DomainValidationError("Password hash cannot be empty")
        self._password_hash = new_hash.strip()
        self._touch()

    def deactivate(self) -> None:
        if self._is_active:
            self._is_active = False
            self._touch()

    def record_login(self) -> None:
        self._last_login = get_utc_now()
        self._touch()

    def _touch(self) -> None:
        self._updated_at = get_utc_now()

    def __repr__(self) -> str:
        return f"<User {self._username} ({self._id})>"
