from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, Path, Request, UploadFile, Header, status

from shop.app.api.mappers.uploads import map_upload_file
from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.pagination import CommonPaginationParams
from shop.app.dependencies.services import (
    get_event_log_service,
    get_product_service,
    get_product_presenter,
)
from shop.app.models.schemas import (
    ProductCreate,
    ProductUpdate,
    UserOut,
    ProductOut,
)
from shop.app.api.presenters.product_presenter import ProductPresenter
from shop.app.services.event_log_service import EventLogService
from shop.app.services.product_service import ProductService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductOut,
)
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
    presenter: ProductPresenter = Depends(get_product_presenter),
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
    product = await product_service.create_product(data, source)

    await event_log_service.log_event(
        "PRODUCT_CREATED",
        user_id=current_user.id,
        description=f"Product #{product.id} created by {current_user.username}",
        request=request,
    )

    return presenter.to_out(product)


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductOut,
)
async def get_product_by_id(
    product_id: int = Path(..., gt=0),
    product_service: ProductService = Depends(get_product_service),
    presenter: ProductPresenter = Depends(get_product_presenter),
):
    product = await product_service.get_product_by_id(product_id)
    return presenter.to_out(product)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[ProductOut],
)
async def get_all_products(
    product_service: ProductService = Depends(get_product_service),
    pagination: CommonPaginationParams = Depends(CommonPaginationParams),
    presenter: ProductPresenter = Depends(get_product_presenter),
):
    products = await product_service.get_all_products(pagination.limit, pagination.offset)
    return presenter.to_out_list(products)


@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductOut,
)
async def update_product(
    request: Request,
    product_id: int = Path(..., gt=0),
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
    presenter: ProductPresenter = Depends(get_product_presenter),
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
    product = await product_service.update_product(product_id, data, source)

    await event_log_service.log_event(
        "PRODUCT_UPDATED",
        user_id=current_user.id,
        description=f"Product #{product_id} updated by {current_user.username}",
        request=request,
    )

    return presenter.to_out(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_product(
    request: Request,
    product_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    await product_service.delete_product(product_id)

    await event_log_service.log_event(
        "PRODUCT_DELETED",
        user_id=current_user.id,
        description=f"Product #{product_id} deleted by {current_user.username}",
        request=request,
    )
