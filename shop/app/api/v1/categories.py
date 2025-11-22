from fastapi import APIRouter, Depends, Body, Path, Request
from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_category_service, get_event_log_service
from shop.app.schemas.category_schemas import CategoryResponse, CategoryCreate, CategoryUpdate
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.category_service import CategoryService
from shop.app.services.event_log_service import EventLogService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix='/categories', tags=['Categories'])


@router.post("/", response_model=CategoryResponse)
async def create_category(request: Request,
                          data: CategoryCreate = Body(),
                          current_user: UserOut = Depends(get_current_user),
                          category_service: CategoryService = Depends(get_category_service),
                          event_log_service: EventLogService = Depends(get_event_log_service)):
    _ensure_admin(current_user)
    response = await category_service.create_category(data)
    await event_log_service.log_event(
        "CATEGORY_CREATED",
        user_id=current_user.id,
        description=f"Category #{response['id']} created by {current_user.username}",
        request=request,
    )
    return response


@router.get("/{category_id}")
async def get_category_by_id(category_id: int = Path(),
                             category_service: CategoryService = Depends(get_category_service)):
    return await category_service.get_category_by_id(category_id)


@router.get("/")
async def get_all_categories(category_service: CategoryService = Depends(get_category_service)):
    return await category_service.get_all_categories()


@router.put("/{category_id}")
async def update_category(request: Request,
                          category_id: int = Path(),
                          data: CategoryUpdate = Body(),
                          current_user: UserOut = Depends(get_current_user),
                          category_service: CategoryService = Depends(get_category_service),
                          event_log_service: EventLogService = Depends(get_event_log_service)):
    _ensure_admin(current_user)
    response = await category_service.update_category(category_id, data)
    await event_log_service.log_event(
        "CATEGORY_UPDATED",
        user_id=current_user.id,
        description=f"Category #{category_id} updated by {current_user.username}",
        request=request,
    )
    return response


@router.delete("/{category_id}")
async def delete_category(request: Request,
                          category_id: int = Path(),
                          current_user: UserOut = Depends(get_current_user),
                          category_service: CategoryService = Depends(get_category_service),
                          event_log_service: EventLogService = Depends(get_event_log_service)):
    _ensure_admin(current_user)
    response = await category_service.delete_category(category_id)
    await event_log_service.log_event(
        "CATEGORY_DELETED",
        user_id=current_user.id,
        description=f"Category #{category_id} deleted by {current_user.username}",
        request=request,
    )
    return response
