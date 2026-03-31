from datetime import datetime, timedelta, timezone

from shop.app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    NotFoundError,
    OperationFailedError,
    PermissionDeniedError,
    ServiceUnavailableError,
)
from shop.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from shop.app.core.config import settings
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.cache_service import CacheService
from shop.app.services.session_service import SessionService
from shop.app.schemas.auth_schemas import (
    AuthResponse,
    AuthUserOut,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    TokenPair,
)
from shop.app.schemas.user_schemas import UserOut


class AuthService:
    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheService,
        session_service: SessionService,
    ):
        self._uow = uow
        self._cache = cache
        self._session_service = session_service

    # ---------- Public API ----------

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        async with self._uow as uow:
            await self._ensure_unique_credentials(uow, payload.username, payload.email)
            await self._ensure_default_role_exists(uow)
            user = await self._create_user_with_default_role(uow, payload)
            await uow.commit()
        return RegisterResponse(
            message="Registration successful",
            user=self._to_auth_user(user),
        )

    async def login(
        self,
        payload: LoginRequest,
        ip_address: str = "",
        user_agent: str = "",
    ) -> AuthResponse:
        async with self._uow as uow:
            user = await self._authenticate_user(uow, payload)
            await self._cache.reset_failed_attempts(payload.username)
            self._ensure_user_active(user)

            safe_user = await self._reload_user(uow, user.id)
            session_id = await self._session_service.create_session(
                safe_user, ip_address=ip_address, user_agent=user_agent,
            )
            tokens = await self._issue_tokens(uow, safe_user, session_id=session_id)
            await uow.commit()

        return AuthResponse(user=self._to_auth_user(safe_user), tokens=tokens)

    async def refresh(self, payload: RefreshRequest) -> RefreshResponse:
        token_data = self._decode_and_validate_refresh_token(payload.refresh_token)

        async with self._uow as uow:
            token_hash = hash_token(payload.refresh_token)
            stored_token = await self._get_refresh_session_or_unauthorized(uow, token_hash)

            user = await self._get_user_for_refresh(uow, stored_token.user_id, token_data)
            await uow.refresh_tokens.delete(stored_token.id)

            old_session_id = token_data.get("sid")
            if old_session_id:
                await self._session_service.delete_session(old_session_id)

            session_id = await self._session_service.create_session(user)
            tokens = await self._issue_tokens(uow, user, session_id=session_id)
            await uow.commit()

        return RefreshResponse(**tokens.model_dump())

    async def logout(self, payload: LogoutRequest, session_id: str | None = None) -> None:
        async with self._uow as uow:
            token_hash = hash_token(payload.refresh_token)
            rows = await uow.refresh_tokens.delete_by_hash(token_hash)
            if not rows:
                stored = await uow.refresh_tokens.get_by_hash(token_hash)
                if stored:
                    await uow.refresh_tokens.delete(stored.id)
            await uow.commit()

        if session_id:
            await self._session_service.delete_session(session_id)

    # ---------- Internal helpers ----------

    @staticmethod
    async def _ensure_unique_credentials(uow: UnitOfWork, username: str, email: str) -> None:
        if await uow.users.exists_with_username(username):
            raise AlreadyExistsError("Username")
        if await uow.users.exists_with_email(email):
            raise AlreadyExistsError("Email")

    @staticmethod
    async def _ensure_default_role_exists(uow: UnitOfWork) -> None:
        default_role = await uow.roles.get_by_id(settings.DEFAULT_USER_ROLE_ID)
        if not default_role:
            raise ServiceUnavailableError(
                f"Registration is temporarily unavailable: default user role "
                f"(id={settings.DEFAULT_USER_ROLE_ID}) is not configured. "
                "Please contact the administrator."
            )

    @staticmethod
    async def _create_user_with_default_role(
        uow: UnitOfWork,
        payload: RegisterRequest,
    ) -> UserOut:
        user_id = await uow.users.create(
            {
                "username": payload.username,
                "email": payload.email,
                "password_hash": hash_password(payload.password),
                "full_name": payload.full_name,
                "is_active": True,
                "role": settings.DEFAULT_USER_ROLE_ID,
                "last_login": datetime.now(timezone.utc).replace(tzinfo=None),
            }
        )
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise OperationFailedError("Unable to fetch created user")
        return user

    async def _authenticate_user(self, uow: UnitOfWork, payload: LoginRequest) -> UserOut:
        if await self._cache.is_blacklisted(payload.username):
            raise PermissionDeniedError(
                "Account temporarily blocked due to too many failed login "
                f"attempts. Please try again in {settings.BLOCK_TIME_MINUTES} minutes."
            )

        user = await uow.users.get_by_username(payload.username)
        if not user or not verify_password(payload.password, user.password_hash):
            await self._handle_failed_attempt(payload.username)
            raise AuthenticationError("Incorrect username or password")

        return user

    @staticmethod
    def _ensure_user_active(user: UserOut) -> None:
        if not user.is_active:
            raise PermissionDeniedError("User is disabled")

    @staticmethod
    async def _reload_user(uow: UnitOfWork, user_id: int) -> UserOut:
        await uow.users.update_last_login(
            user_id=user_id,
            last_login=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise OperationFailedError("User not found")
        return user

    @staticmethod
    def _decode_and_validate_refresh_token(refresh_token: str) -> dict:
        try:
            token_data = decode_token(refresh_token)
        except Exception:
            raise AuthenticationError("Invalid refresh token")

        if token_data.get("scope") != "refresh_token":
            raise AuthenticationError("Invalid refresh token scope")

        return token_data

    @staticmethod
    async def _get_refresh_session_or_unauthorized(uow: UnitOfWork, token_hash: str):
        stored_token = await uow.refresh_tokens.get_by_hash(token_hash)
        if not stored_token:
            raise AuthenticationError("Refresh token revoked")
        return stored_token

    @staticmethod
    async def _get_user_for_refresh(uow: UnitOfWork, user_id: int, token_data: dict) -> UserOut:
        token_user_id = int(token_data.get("sub"))
        if user_id != token_user_id:
            raise AuthenticationError("Refresh token mismatch")

        user = await uow.users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        return user

    async def _handle_failed_attempt(self, username: str) -> None:
        attempts = await self._cache.increment_failed_attempts(username)
        if attempts >= settings.MAX_FAILED_ATTEMPTS:
            await self._cache.add_to_blocklist(
                username=username,
                ttl_minutes=settings.BLOCK_TIME_MINUTES,
            )

    @staticmethod
    def _to_auth_user(user: UserOut) -> AuthUserOut:
        return AuthUserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role_id=user.role_id,
            role_name=user.role_name,
        )

    @staticmethod
    async def _issue_tokens(
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

        expires_at = (datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )).replace(tzinfo=None)
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
