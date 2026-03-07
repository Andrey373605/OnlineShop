from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from shop.app.core.config import settings
from shop.app.core.security import decode_token
from shop.app.dependencies.cache import get_cache_service
from shop.app.dependencies.repositories import get_user_repository
from shop.app.repositories.user_repository import UserRepository
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.cache_service import CacheService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
    cache: CacheService = Depends(get_cache_service),
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

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user_id = int(user_id_raw)

    cached = await cache.get_user_session(user_id)
    if cached is not None:
        user = UserOut.model_validate_json(cached)
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User is disabled")
        return user

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is disabled")

    await cache.set_user_session(
        user.id,
        user.model_dump_json(),
        settings.USER_SESSION_CACHE_TTL_SECONDS,
    )
    return user


