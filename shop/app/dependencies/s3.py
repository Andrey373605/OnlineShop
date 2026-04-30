import uuid

from fastapi import Request

from shop.app.adapters.s3.filename_gen import UUIDFilenameGenerator
from shop.app.adapters.s3.validator import FileValidator, FileValidationRules
from shop.app.core.config import settings
from shop.app.core.ports.base import HealthCheckPort
from shop.app.core.ports.file_storage import FileStoragePort
from shop.app.core.state import get_app_state
from shop.app.utils.get_utc_now import get_utc_now


async def get_storage_service(request: Request) -> FileStoragePort:
    return get_app_state(request).storage


async def get_storage_readiness(request: Request) -> HealthCheckPort:
    return get_app_state(request).storage_readiness


async def get_file_validator() -> FileValidator:
    return FileValidator(
        FileValidationRules(
            max_size_bytes=settings.IMAGE_MAX_SIZE_BYTES,
            allowed_extensions=settings.IMAGE_ALLOWED_EXTENSIONS,
        )
    )


async def get_filename_generator() -> UUIDFilenameGenerator:
    return UUIDFilenameGenerator(
        date_format="%Y/%m/%d",
        time_provider=get_utc_now,
        uuid_provider=(lambda: uuid.uuid4().hex),
    )
