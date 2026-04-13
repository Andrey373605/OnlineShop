from shop.app.core.exceptions import AuthenticationError, PermissionDeniedError
from shop.app.core.security import verify_password
from shop.app.models.schemas import (
    AuthResponse,
    AuthUserOut,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    UserOut,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.services.auth.auth_protection_service import AuthProtectionService
from shop.app.services.auth.auth_session_service import AuthSessionService
from shop.app.services.auth.auth_token_service import AuthTokenService
from shop.app.utils.generate_token import generate_token
from shop.app.utils.get_utc_now import get_utc_now


class AuthLoginService:
    """Сервис логина и ротации auth-сессий."""

    def __init__(
        self,
        uow: UnitOfWork,
        session_service: AuthSessionService,
        token_service: AuthTokenService,
        protection_service: AuthProtectionService,
    ) -> None:
        self._uow = uow
        self._session_service = session_service
        self._token_service = token_service
        self._protection_service = protection_service

    async def login(
        self,
        payload: LoginRequest,
        ip_address: str = "",
        user_agent: str = "",
    ) -> AuthResponse:
        async with self._uow as uow:
            user = await self._get_authenticated_user(uow, payload)

            session_id = generate_token()
            tokens = await self._token_service.issue_tokens(uow, user, session_id)
            await uow.users.update_last_login(user.id, get_utc_now())
            await uow.commit()

        await self._finalize_session_creation(user, session_id, ip_address, user_agent)
        return AuthResponse(user=self._to_auth_user(user), tokens=tokens)

    async def refresh(self, payload: RefreshRequest) -> RefreshResponse:
        token_data = self._token_service.decode_and_validate_refresh_token(
            payload.refresh_token
        )
        new_session_id = generate_token()

        async with self._uow as uow:
            user, tokens = await self._rotate_db_token(
                uow, payload.refresh_token, token_data, new_session_id
            )
            await uow.commit()

        await self._rotate_external_session(
            user, old_session_id=token_data.get("sid"), new_session_id=new_session_id
        )
        return RefreshResponse(**tokens.model_dump())

    async def logout(
        self, payload: LogoutRequest, session_id: str | None = None
    ) -> None:
        async with self._uow as uow:
            await self._token_service.revoke_refresh_token(uow, payload.refresh_token)
            await uow.commit()

        refresh_session_id = self._token_service.extract_session_id_from_refresh_token(
            payload.refresh_token
        )
        session_ids = {sid for sid in (session_id, refresh_session_id) if sid}
        for sid in session_ids:
            await self._session_service.delete_session(sid)

    async def _get_authenticated_user(self, uow: UnitOfWork, payload: LoginRequest):
        await self._protection_service.ensure_login_allowed(payload.username)
        user = await uow.users.get_by_username(payload.username)

        if not self._is_valid_credentials(user, payload.password):
            await self._handle_auth_failure(payload.username)

        self._ensure_user_active(user)
        return user

    async def _finalize_session_creation(
        self, user: UserOut, session_id: str, ip_address: str, user_agent: str
    ):
        await self._protection_service.reset_failed_attempts(user.username)
        await self._session_service.create_session(
            user=user,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def _rotate_external_session(
        self, user: UserOut, old_session_id: str | None, new_session_id: str
    ):
        await self._session_service.ensure_new_session_created(user, new_session_id)
        await self._session_service.delete_session_if_present(old_session_id)

    async def _rotate_db_token(
        self, uow: UnitOfWork, raw_token: str, token_data: dict, new_sid: str
    ):
        stored_token = await self._token_service.get_refresh_session_or_unauthorized(
            uow, raw_token
        )
        user = await self._token_service.get_user_for_refresh(
            uow, stored_token.user_id, token_data
        )

        tokens = await self._token_service.rotate_refresh_token(
            uow, stored_token.id, user, new_sid
        )
        return user, tokens

    async def _handle_auth_failure(self, username: str):
        await self._protection_service.register_failed_attempt(username)
        raise AuthenticationError("Incorrect username or password")

    @staticmethod
    def _is_valid_credentials(user: UserOut, password: str):
        return user is not None and verify_password(password, user.password_hash)

    @staticmethod
    def _ensure_user_active(user: UserOut) -> None:
        if not user.is_active:
            raise PermissionDeniedError("User is disabled")

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
