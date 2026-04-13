from shop.app.models.schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
)
from shop.app.services.auth.auth_login_service import AuthLoginService
from shop.app.services.auth.auth_registration_service import AuthRegistrationService


class AuthService:
    def __init__(
        self,
        registration_service: AuthRegistrationService,
        login_service: AuthLoginService,
    ) -> None:
        self._registration_service = registration_service
        self._login_service = login_service

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        return await self._registration_service.register(payload)

    async def login(
        self,
        payload: LoginRequest,
        ip_address: str = "",
        user_agent: str = "",
    ) -> AuthResponse:
        return await self._login_service.login(
            payload=payload,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def refresh(self, payload: RefreshRequest) -> RefreshResponse:
        return await self._login_service.refresh(payload)

    async def logout(
        self, payload: LogoutRequest, session_id: str | None = None
    ) -> None:
        await self._login_service.logout(payload=payload, session_id=session_id)
