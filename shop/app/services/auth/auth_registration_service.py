from shop.app.core.config import settings
from shop.app.core.exceptions import (
    AlreadyExistsError,
    OperationFailedError,
    ServiceUnavailableError,
)
from shop.app.utils.security import hash_password
from shop.app.models.schemas import (
    AuthUserOut,
    RegisterRequest,
    RegisterResponse,
    UserOut,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.utils.get_utc_now import get_utc_now


class AuthRegistrationService:
    """Сервис регистрации пользователей."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

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
                "last_login": get_utc_now(),
            }
        )
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise OperationFailedError("Unable to fetch created user")
        return user

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
