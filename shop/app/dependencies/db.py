from fastapi import Request

from shop.app.repositories.protocols import UnitOfWork
from shop.app.repositories.unit_of_work import SqlUnitOfWork


async def get_db(request: Request):
    """Выдаёт соединение из пула; пул берётся из app.state.db_pool (устанавливается в lifespan)."""
    request.state.used_db = True
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        yield conn


async def get_uow(request: Request) -> UnitOfWork:
    """Фабрика UnitOfWork — передаёт пул, транзакцию открывает сервис через ``async with``."""
    request.state.used_db = True
    return SqlUnitOfWork(pool=request.app.state.db_pool)
