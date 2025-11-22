from fastapi import APIRouter, Body, Depends, Path, Query, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_event_log_service, get_user_service
from shop.app.schemas.user_schemas import UserCreate, UserOut, UserUpdate
from shop.app.services.event_log_service import EventLogService
from shop.app.services.user_service import UserService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/users", tags=["Users"])



@router.get(
    "/",
    response_model=list[UserOut],
)
async def list_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[UserOut]:
    _ensure_admin(current_user)
    return await service.list_users(limit=limit, offset=offset)


@router.get(
    "/{user_id}",
    response_model=UserOut,
)
async def get_user_by_id(
    user_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserOut:
    _ensure_admin(current_user)
    return await service.get_user_by_id(user_id)


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request,
    data: UserCreate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> UserOut:
    _ensure_admin(current_user)
    user = await service.create_user(data)
    await event_log_service.log_event(
        "USER_CREATED",
        user_id=current_user.id,
        description=f"User #{user.id} created by {current_user.username}",
        request=request,
    )
    return user


@router.put(
    "/{user_id}",
    response_model=UserOut,
)
async def update_user(
    request: Request,
    user_id: int = Path(..., gt=0),
    data: UserUpdate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> UserOut:
    _ensure_admin(current_user)
    user = await service.update_user(user_id, data)
    await event_log_service.log_event(
        "USER_UPDATED",
        user_id=current_user.id,
        description=f"User #{user_id} updated by {current_user.username}",
        request=request,
    )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    request: Request,
    user_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    _ensure_admin(current_user)
    await service.delete_user(user_id)
    await event_log_service.log_event(
        "USER_DELETED",
        user_id=current_user.id,
        description=f"User #{user_id} deleted by {current_user.username}",
        request=request,
    )



