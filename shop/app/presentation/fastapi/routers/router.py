from fastapi import APIRouter

from shop.app.presentation.fastapi.routers import (
    categories,
    orders,
    product_images,
)
from shop.app.presentation.fastapi.routers import (
    roles,
    cart,
    auth,
    products,
    users,
    product_specifications,
    reviews,
)


def get_api_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    router.include_router(auth.router)
    router.include_router(categories.router)
    router.include_router(products.router)
    router.include_router(cart.router)
    router.include_router(product_images.router)
    router.include_router(product_specifications.router)
    router.include_router(roles.router)
    router.include_router(users.router)
    router.include_router(orders.router)
    router.include_router(reviews.router)

    return router
