from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from shop.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from shop.app.core.config import settings
from shop.app.repositories.protocols import (
    RefreshTokenRepository,
    RoleRepository,
    UserRepository,
)
from shop.app.services.cache_service import CacheService
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
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        role_repo: RoleRepository,
        cache: CacheService,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.role_repo = role_repo
        self.cache = cache

    # ---------- Public API ----------

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        await self._ensure_unique_credentials(payload.username, payload.email)
        await self._ensure_default_role_exists()

        user = await self._create_user_with_default_role(payload)
        return RegisterResponse(
            message="Registration successful",
            user=self._to_auth_user(user),
        )

    async def login(self, payload: LoginRequest) -> AuthResponse:
        user = await self._authenticate_user(payload)
        await self.cache.reset_failed_attempts(payload.username)
        self._ensure_user_active(user)

        safe_user = await self._reload_user(user.id)
        tokens = await self._issue_tokens(safe_user)
        await self.cache.set_user_session(
            safe_user.id,
            safe_user.model_dump_json(),
            settings.USER_SESSION_CACHE_TTL_SECONDS,
        )
        return AuthResponse(user=self._to_auth_user(safe_user), tokens=tokens)

    async def refresh(self, payload: RefreshRequest) -> RefreshResponse:
        token_data = self._decode_and_validate_refresh_token(payload.refresh_token)

        token_hash = hash_token(payload.refresh_token)
        stored_token = await self._get_refresh_session_or_unauthorized(token_hash)

        user = await self._get_user_for_refresh(stored_token.user_id, token_data)
        await self.refresh_repo.delete(stored_token.id)

        tokens = await self._issue_tokens(user)
        await self.cache.set_user_session(
            user.id,
            user.model_dump_json(),
            settings.USER_SESSION_CACHE_TTL_SECONDS,
        )
        return RefreshResponse(**tokens.model_dump())

    async def logout(self, payload: LogoutRequest) -> None:
        token_hash = hash_token(payload.refresh_token)
        rows = await self.refresh_repo.delete_by_hash(token_hash)
        if not rows:
            stored = await self.refresh_repo.get_by_hash(token_hash)
            if stored:
                await self.refresh_repo.delete(stored.id)

    # ---------- Internal helpers ----------

    async def _ensure_unique_credentials(self, username: str, email: str) -> None:
        if await self.user_repo.exists_with_username(username):
            raise HTTPException(status_code=400, detail="Username already exists")

        if await self.user_repo.exists_with_email(email):
            raise HTTPException(status_code=400, detail="Email already exists")

    async def _ensure_default_role_exists(self) -> None:
        default_role = await self.role_repo.get_by_id(settings.DEFAULT_USER_ROLE_ID)
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"Registration is temporarily unavailable: default user role "
                    f"(id={settings.DEFAULT_USER_ROLE_ID}) is not configured. "
                    "Please contact the administrator."
                ),
            )

    async def _create_user_with_default_role(
        self,
        payload: RegisterRequest,
    ) -> UserOut:
        user_id = await self.user_repo.create(
            {
                "username": payload.username,
                "email": payload.email,
                "password_hash": hash_password(payload.password),
                "full_name": payload.full_name,
                "is_active": True,
                "role": settings.DEFAULT_USER_ROLE_ID,
                "last_login": datetime.now(),
            }
        )
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to fetch created user",
            )
        return user

    async def _authenticate_user(self, payload: LoginRequest) -> UserOut:
        if await self.cache.is_blacklisted(payload.username):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Account temporarily blocked due to too many failed login "
                    f"attempts. Please try again in {settings.BLOCK_TIME_MINUTES} minutes."
                ),
            )

        user = await self.user_repo.get_by_username(payload.username)
        if not user or not verify_password(payload.password, user.password_hash):
            await self._handle_failed_attempt(payload.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        return user

    @staticmethod
    def _ensure_user_active(user: UserOut) -> None:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is disabled",
            )

    async def _reload_user(self, user_id: int) -> UserOut:
        await self.user_repo.update_last_login(
            user_id,
            last_login=datetime.now(),
        )
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User not found",
            )
        return user

    def _decode_and_validate_refresh_token(self, refresh_token: str) -> dict:
        try:
            token_data = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if token_data.get("scope") != "refresh_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token scope",
            )

        return token_data

    async def _get_refresh_session_or_unauthorized(self, token_hash: str):
        stored_token = await self.refresh_repo.get_by_hash(token_hash)
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked",
            )
        return stored_token

    async def _get_user_for_refresh(self, user_id: int, token_data: dict) -> UserOut:
        token_user_id = int(token_data.get("sub"))
        if user_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token mismatch",
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def _handle_failed_attempt(self, username: str) -> None:
        attempts = await self.cache.increment_failed_attempts(username)
        if attempts >= settings.MAX_FAILED_ATTEMPTS:
            await self.cache.add_to_blocklist(
                username,
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

    async def _issue_tokens(self, user: UserOut) -> TokenPair:
        access_token = create_access_token(
            subject=str(user.id),
            extra_data={"username": user.username},
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            extra_data={"username": user.username},
        )

        await self._store_refresh_token(user.id, refresh_token)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    async def _store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        expires_at = datetime.now() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.refresh_repo.create(
            {
                "user_id": user_id,
                "token_hash": hash_token(refresh_token),
                "expires_at": expires_at,
            }
        )

