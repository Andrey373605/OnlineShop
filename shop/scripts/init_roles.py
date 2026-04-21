import asyncio

import asyncpg

from shop.app.core.config import settings

DEFAULT_ROLES = [
    "admin",
    "user",
]


async def init_roles() -> None:
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        for name in DEFAULT_ROLES:
            await conn.execute(
                """
                INSERT INTO roles (name)
                VALUES ($1)
                ON CONFLICT (name) DO NOTHING
                """,
                name,
            )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_roles())

