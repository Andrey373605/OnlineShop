from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, Path, Request, UploadFile, Header

from shop.app.api.mappers.uploads import map_upload_file
from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.pagination import CommonPaginationParams
from shop.app.dependencies.services import get_event_log_service, get_product_service
from shop.app.models.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    UserOut,
)
from shop.app.services.event_log_service import EventLogService
from shop.app.services.product_service import ProductService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    price: Decimal = Form(...),
    stock: int = Form(...),
    brand: str = Form(...),
    is_published: bool = Form(...),
    category_id: int = Form(...),
    thumbnail: UploadFile = File(...),
    content_length: int = Header(None),
    current_user: UserOut = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    data = ProductCreate(
        title=title,
        description=description,
        price=price,
        stock=stock,
        brand=brand,
        is_published=is_published,
        category_id=category_id,
    )
    source = map_upload_file(thumbnail, content_length)
    response = await product_service.create_product(data, source)
    await event_log_service.log_event(
        "PRODUCT_CREATED",
        user_id=current_user.id,
        description=f"Product #{response['id']} created by {current_user.username}",
        request=request,
    )
    return response


@router.get("/{product_id}")
async def get_product_by_id(
    product_id: int = Path(),
    product_service: ProductService = Depends(get_product_service),
):
    return await product_service.get_product_by_id(product_id)


@router.get("/")
async def get_all_products(
    product_service: ProductService = Depends(get_product_service),
    pagination: CommonPaginationParams = Depends(CommonPaginationParams),
):
    return await product_service.get_all_products(pagination.limit, pagination.offset)


@router.put("/{product_id}")
async def update_product(
    request: Request,
    product_id: int = Path(),
    title: str = Form(...),
    description: str = Form(...),
    price: Decimal = Form(...),
    stock: int = Form(...),
    brand: str = Form(...),
    is_published: bool = Form(...),
    category_id: int = Form(...),
    thumbnail: UploadFile | None = File(None),
    content_length: int = Header(None),
    current_user: UserOut = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    data = ProductUpdate(
        title=title,
        description=description,
        price=price,
        stock=stock,
        brand=brand,
        is_published=is_published,
        category_id=category_id,
    )
    source = map_upload_file(thumbnail, content_length) if thumbnail else None
    response = await product_service.update_product(product_id, data, source)
    await event_log_service.log_event(
        "PRODUCT_UPDATED",
        user_id=current_user.id,
        description=f"Product #{product_id} updated by {current_user.username}",
        request=request,
    )
    return response


@router.delete("/{product_id}")
async def delete_product(
    request: Request,
    product_id: int = Path(),
    current_user: UserOut = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await product_service.delete_product(product_id)
    await event_log_service.log_event(
        "PRODUCT_DELETED",
        user_id=current_user.id,
        description=f"Product #{product_id} deleted by {current_user.username}",
        request=request,
    )
    return response
