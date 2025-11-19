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
from shop.app.repositories.refresh_token_repository import RefreshTokenRepository
from shop.app.repositories.user_repository import UserRepository
from shop.app.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenPair,
)
from shop.app.schemas.user_schemas import UserOut


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        if await self.user_repo.exists_with_username(payload.username):
            raise HTTPException(status_code=400, detail="Username already exists")

        if await self.user_repo.exists_with_email(payload.email):
            raise HTTPException(status_code=400, detail="Email already exists")



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
            raise HTTPException(status_code=500, detail="Unable to fetch created user")

        tokens = await self._issue_tokens(user)
        return AuthResponse(user=user, tokens=tokens)

    async def login(self, payload: LoginRequest) -> AuthResponse:
        user = await self.user_repo.get_by_username(payload.username)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="User is disabled")

        await self.user_repo.update_last_login(
            user.id,
            last_login=datetime.now()
        )

        # Reload without password hash
        safe_user = await self.user_repo.get_by_id(user.id)
        if not safe_user:
            raise HTTPException(status_code=500, detail="User not found")

        tokens = await self._issue_tokens(safe_user)
        return AuthResponse(user=safe_user, tokens=tokens)

    async def refresh(self, payload: RefreshRequest) -> RefreshResponse:
        try:
            token_data = decode_token(payload.refresh_token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if token_data.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid refresh token scope")

        token_hash = hash_token(payload.refresh_token)
        stored_token = await self.refresh_repo.get_by_hash(token_hash)
        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        user_id = int(token_data.get("sub"))
        if stored_token.user_id != user_id:
            raise HTTPException(status_code=401, detail="Refresh token mismatch")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Revoke old refresh token
        await self.refresh_repo.delete(stored_token.id)

        tokens = await self._issue_tokens(user)
        return RefreshResponse(**tokens.model_dump())

    async def logout(self, payload: LogoutRequest) -> None:
        token_hash = hash_token(payload.refresh_token)
        rows = await self.refresh_repo.delete_by_hash(token_hash)
        if not rows:
            stored = await self.refresh_repo.get_by_hash(token_hash)
            if stored:
                await self.refresh_repo.delete(stored.id)

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

