from fastapi import Request


async def get_db(request: Request):
    """Выдаёт соединение из пула; пул берётся из app.state.db_pool (устанавливается в lifespan)."""
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        yield conn
