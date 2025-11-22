from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_auth_service, get_event_log_service
from shop.app.services.event_log_service import EventLogService
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
from shop.app.services.auth_service import AuthService
from shop.app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> AuthResponse:
    response = await auth_service.register(payload)
    await event_log_service.log_event(
        "AUTH_REGISTER",
        user_id=response.user.id,
        description=f"User {response.user.username} registered",
        request=request,
    )
    return response


@router.post("/login", response_model=AuthResponse)
async def login_user(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> AuthResponse:
    response = await auth_service.login(payload)
    await event_log_service.log_event(
        "AUTH_LOGIN",
        user_id=response.user.id,
        description=f"User {response.user.username} logged in",
        request=request,
    )
    return response


@router.post("/token", response_model=TokenPair)
async def login_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> TokenPair:
    payload = LoginRequest(username=form_data.username, password=form_data.password)
    auth_response = await auth_service.login(payload)
    await event_log_service.log_event(
        "AUTH_LOGIN",
        user_id=auth_response.user.id,
        description=f"User {auth_response.user.username} logged in via form",
        request=request,
    )
    return auth_response.tokens


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_tokens(
    payload: RefreshRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> RefreshResponse:
    response = await auth_service.refresh(payload)
    user_id = None
    try:
        token_data = decode_token(payload.refresh_token)
        user_id = int(token_data.get("sub"))
    except Exception:
        user_id = None
    await event_log_service.log_event(
        "AUTH_REFRESH",
        user_id=user_id,
        description="Refresh token exchanged",
        request=request,
    )
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    payload: LogoutRequest,
    request: Request,
    current_user: UserOut = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    await auth_service.logout(payload)
    await event_log_service.log_event(
        "AUTH_LOGOUT",
        user_id=current_user.id,
        description=f"User {current_user.username} logged out",
        request=request,
    )


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user
