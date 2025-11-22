from fastapi import APIRouter, Body, Depends, Path, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_event_log_service, get_role_service
from shop.app.schemas.role_schemas import RoleCreate, RoleOut, RoleResponse, RoleUpdate
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.role_service import RoleService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    request: Request,
    data: RoleCreate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> RoleResponse:
    _ensure_admin(current_user)
    response = await role_service.create_role(data)
    await event_log_service.log_event(
        "ROLE_CREATED",
        user_id=current_user.id,
        description=f"Role #{response.id} created by {current_user.username}",
        request=request,
    )
    return response


@router.get(
    "/{role_id}",
    response_model=RoleOut,
)
async def get_role_by_id(
    role_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> RoleOut:
    _ensure_admin(current_user)
    return await role_service.get_role_by_id(role_id)


@router.get(
    "/",
    response_model=list[RoleOut],
)
async def get_all_roles(
    current_user: UserOut = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
) -> list[RoleOut]:
    _ensure_admin(current_user)
    return await role_service.get_all_roles()


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
)
async def update_role(
    request: Request,
    role_id: int = Path(..., gt=0),
    data: RoleUpdate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> RoleResponse:
    _ensure_admin(current_user)
    response = await role_service.update_role(role_id, data)
    await event_log_service.log_event(
        "ROLE_UPDATED",
        user_id=current_user.id,
        description=f"Role #{role_id} updated by {current_user.username}",
        request=request,
    )
    return response


@router.delete(
    "/{role_id}",
    response_model=RoleResponse,
)
async def delete_role(
    request: Request,
    role_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> RoleResponse:
    _ensure_admin(current_user)
    response = await role_service.delete_role(role_id)
    await event_log_service.log_event(
        "ROLE_DELETED",
        user_id=current_user.id,
        description=f"Role #{role_id} deleted by {current_user.username}",
        request=request,
    )
    return response



