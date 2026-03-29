from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from shop.app.dependencies.auth import get_current_user, oauth2_scheme
from shop.app.dependencies.services import get_auth_service, get_event_log_service
from shop.app.dependencies.session import get_session_service
from shop.app.schemas.event_log_schemas import EventType
from shop.app.schemas.session_schemas import SessionInfo, SessionListResponse
from shop.app.services.event_log_service import EventLogService
from shop.app.schemas.auth_schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    TokenPair,
)
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.auth_service import AuthService
from shop.app.services.session_service import SessionService
from shop.app.core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])


def _extract_session_id(token: str) -> str | None:
    try:
        payload = decode_token(token)
        return payload.get("sid")
    except Exception:
        return None


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: RegisterRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> RegisterResponse:
    response = await auth_service.register(payload)
    await event_log_service.log_event(
        EventType.AUTH_REGISTER,
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
    ip = request.client.host if request.client else ""
    ua = request.headers.get("user-agent", "")
    response = await auth_service.login(payload, ip_address=ip, user_agent=ua)
    await event_log_service.log_event(
        EventType.AUTH_LOGIN,
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
    ip = request.client.host if request.client else ""
    ua = request.headers.get("user-agent", "")
    auth_response = await auth_service.login(payload, ip_address=ip, user_agent=ua)
    await event_log_service.log_event(
        EventType.AUTH_LOGIN,
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
        EventType.AUTH_REFRESH,
        user_id=user_id,
        description="Refresh token exchanged",
        request=request,
    )
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    payload: LogoutRequest,
    request: Request,
    token: str = Depends(oauth2_scheme),
    current_user: UserOut = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    session_id = _extract_session_id(token)
    await auth_service.logout(payload, session_id=session_id)
    await event_log_service.log_event(
        EventType.AUTH_LOGOUT,
        user_id=current_user.id,
        description=f"User {current_user.username} logged out",
        request=request,
    )


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    return current_user


# ---------- Session management ----------


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: UserOut = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
) -> SessionListResponse:
    raw_sessions = await session_service.get_active_sessions(current_user.id)
    sessions = [SessionInfo.from_redis(s) for s in raw_sessions]
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_session(
    session_id: str,
    request: Request,
    token: str = Depends(oauth2_scheme),
    current_user: UserOut = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    target = await session_service.get_session(session_id)
    if not target or int(target["user_id"]) != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    current_sid = _extract_session_id(token)
    if current_sid == session_id:
        raise HTTPException(status_code=400, detail="Cannot revoke the current session")

    await session_service.delete_session(session_id)
    await event_log_service.log_event(
        EventType.AUTH_LOGOUT,
        user_id=current_user.id,
        description=f"User {current_user.username} revoked session {session_id}",
        request=request,
    )
