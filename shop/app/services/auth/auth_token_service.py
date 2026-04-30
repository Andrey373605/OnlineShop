import logging
from datetime import timedelta
from typing import Any

from jose import JWTError

from shop.app.core.config import settings
from shop.app.core.exceptions import AuthenticationError, NotFoundError
from shop.app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from shop.app.models.schemas import TokenPair, UserOut
from shop.app.repositories.protocols import UnitOfWork
from shop.app.utils.get_utc_now import get_utc_now

logger = logging.getLogger(__name__)


class AuthTokenService:
    """Сервис для выпуска и валидации auth-токенов."""

    @staticmethod
    def decode_and_validate_refresh_token(refresh_token: str) -> dict[str, Any]:
        try:
            token_data = decode_token(refresh_token)
        except JWTError as exc:
            raise AuthenticationError("Invalid refresh token") from exc
        except Exception as exc:
            logger.exception("Unexpected refresh token decode failure")
            raise AuthenticationError("Unexpected error while decoding refresh token") from exc

        if token_data.get("scope") != "refresh_token":
            raise AuthenticationError("Invalid refresh token scope")

        return token_data

    @staticmethod
    def extract_session_id_from_refresh_token(refresh_token: str) -> str | None:
        try:
            token_data = decode_token(refresh_token)
        except Exception:
            return None
        if token_data.get("scope") != "refresh_token":
            return None
        session_id = token_data.get("sid")
        if isinstance(session_id, str) and session_id:
            return session_id
        return None

    @staticmethod
    async def issue_tokens(
        uow: UnitOfWork,
        user: UserOut,
        session_id: str | None = None,
    ) -> TokenPair:
        access_token = create_access_token(
            subject=str(user.id),
            extra_data={"username": user.username},
            session_id=session_id,
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            extra_data={"username": user.username, "sid": session_id},
        )

        expires_at = get_utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await uow.refresh_tokens.create(
            {
                "user_id": user.id,
                "token_hash": hash_token(refresh_token),
                "expires_at": expires_at,
            }
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    async def rotate_refresh_token(
        self, uow: UnitOfWork, old_token_id, user: UserOut, new_session_id: str
    ):
        await uow.refresh_tokens.delete(old_token_id)

        return await self.issue_tokens(uow, user, new_session_id)

    @staticmethod
    async def get_refresh_session_or_unauthorized(uow: UnitOfWork, refresh_token: str) -> Any:
        token_hash = hash_token(refresh_token)
        stored_token = await uow.refresh_tokens.get_by_hash(token_hash)
        if not stored_token:
            raise AuthenticationError("Refresh token revoked")
        return stored_token

    @staticmethod
    async def get_user_for_refresh(
        uow: UnitOfWork, user_id: int, token_data: dict[str, Any]
    ) -> UserOut:
        token_subject = token_data.get("sub")
        if token_subject is None:
            raise AuthenticationError("Invalid refresh token subject")

        try:
            token_user_id = int(token_subject)
        except (TypeError, ValueError) as exc:
            raise AuthenticationError("Invalid refresh token subject") from exc

        if user_id != token_user_id:
            raise AuthenticationError("Refresh token mismatch")

        user = await uow.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        return user

    @staticmethod
    async def revoke_refresh_token(uow: UnitOfWork, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)
        rows = await uow.refresh_tokens.delete_by_hash(token_hash)
        if rows:
            return
        stored = await uow.refresh_tokens.get_by_hash(token_hash)
        if not stored:
            return
        await uow.refresh_tokens.delete(stored.id)
