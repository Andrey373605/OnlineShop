
import re
from typing import cast

from shop.app.domain.errors import DomainValidationError

_MAX_USERNAME_LEN = 64
_MAX_EMAIL_LEN = 254
_MAX_FULL_NAME_LEN = 200


class Username(str):
    def __new__(cls, value: str) -> Username:
        if not isinstance(value, str):
            raise DomainValidationError("Username must be a string")
        clean = value.strip()
        if len(clean) < 3:
            raise DomainValidationError("Username is too short")
        if len(clean) > _MAX_USERNAME_LEN:
            raise DomainValidationError("Username is too long")
        return cast(Username, str.__new__(cls, clean))


class Email(str):
    def __new__(cls, value: str) -> Email:
        if not isinstance(value, str):
            raise DomainValidationError("Email must be a string")
        clean = value.strip().lower()
        if len(clean) > _MAX_EMAIL_LEN:
            raise DomainValidationError("Email is too long")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", clean):
            raise DomainValidationError(f"Invalid email format: {clean}")
        return cast(Email, str.__new__(cls, clean))


class FullName(str):
    def __new__(cls, value: str) -> FullName:
        if not isinstance(value, str):
            raise DomainValidationError("Full name must be a string")
        clean = value.strip()
        if not clean:
            raise DomainValidationError("Full name cannot be empty")
        if len(clean) > _MAX_FULL_NAME_LEN:
            raise DomainValidationError("Full name is too long")
        return cast(FullName, str.__new__(cls, clean))


__all__ = ["Username", "Email", "FullName"]
