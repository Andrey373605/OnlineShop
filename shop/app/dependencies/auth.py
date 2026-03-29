from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from shop.app.core.security import decode_token
from shop.app.dependencies.session import get_session_service
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.session_service import SessionService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service),
) -> UserOut:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("scope") != "access_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token scope",
        )

    session_id = payload.get("sid")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session in token",
        )

    user = await session_service.get_user_from_session(session_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalidated",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is disabled")

    await session_service.update_activity(session_id)
    return user
