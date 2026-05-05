from fastapi import Request

from shop.app.core.state import get_app_state
from shop.app.infrastructure.persistence.postgres.repositories.unit_of_work import SqlUnitOfWork


async def get_db(request: Request):

    request.state.used_db = True
    pool = get_app_state(request).db_pool
    async with pool.acquire() as conn:
        yield conn


async def get_uow(request: Request) -> SqlUnitOfWork:

    request.state.used_db = True
    return SqlUnitOfWork(pool=get_app_state(request).db_pool)
