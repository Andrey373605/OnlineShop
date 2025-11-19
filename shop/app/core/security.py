from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Any, Optional
import bcrypt
from jose import jwt

from shop.app.core.config import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def _create_token(
    data: dict[str, Any],
    expires_delta: timedelta,
    scope: str,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "scope": scope})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, extra_data: Optional[dict[str, Any]] = None) -> str:
    data = {"sub": subject}
    if extra_data:
        data.update(extra_data)
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, expires_delta, scope="access_token")


def create_refresh_token(subject: str, extra_data: Optional[dict[str, Any]] = None) -> str:
    data = {"sub": subject, "jti": secrets.token_hex(16)}
    if extra_data:
        data.update(extra_data)
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(data, expires_delta, scope="refresh_token")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

