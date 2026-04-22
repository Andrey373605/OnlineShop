from contextlib import asynccontextmanager
from typing import AsyncContextManager, Any

from aiobotocore.session import get_session
from botocore.config import Config


@asynccontextmanager
async def create_aiobotocore_client(
    endpoint_url: str,
    access_key: str,
    secret_key: str,
    config: Config,
) -> AsyncContextManager[Any]:
    """Factory for creating S3 client"""
    session = get_session()
    async with session.create_client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=config,
    ) as client:
        yield client
