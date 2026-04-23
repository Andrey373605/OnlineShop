import io
from unittest.mock import AsyncMock, Mock, patch

import pytest
from botocore.exceptions import ClientError
from fastapi import UploadFile
from starlette.datastructures import Headers

from shop.app.adapters.s3.storage import S3Storage
from shop.app.core.exceptions import DomainValidationError, StorageError, StorageUnavailableError


def _build_storage() -> S3Storage:
    return S3Storage(
        endpoint_url="http://localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket_name="bucket",
        max_file_size=10,
        allowed_extensions={"png", "jpg"},
    )


def _build_upload_file(
    filename: str = "image.png",
    data: bytes = b"12345",
    content_type: str = "image/png",
    size: int | None = 5,
) -> UploadFile:
    return UploadFile(
        file=io.BytesIO(data),
        filename=filename,
        size=size,
        headers=Headers({"content-type": content_type}),
    )


@pytest.mark.asyncio
async def test_upload_file_returns_generated_key() -> None:
    storage = _build_storage()
    file = _build_upload_file()
    storage._validator.validate = Mock()  # type: ignore[method-assign]
    storage._filename_generator.generate = Mock(return_value="generated.png")  # type: ignore[method-assign]
    storage._upload_to_s3 = AsyncMock()  # type: ignore[method-assign]

    result = await storage.upload_file(file, content_length=5)

    assert result == "generated.png"
    storage._validator.validate.assert_called_once_with(file, 5)
    storage._filename_generator.generate.assert_called_once_with(file)
    storage._upload_to_s3.assert_awaited_once_with(file, "generated.png")


@pytest.mark.asyncio
async def test_delete_file_raises_when_key_is_empty() -> None:
    storage = _build_storage()

    with pytest.raises(DomainValidationError, match="Invalid key"):
        await storage.delete_file("")


@pytest.mark.asyncio
async def test_delete_file_calls_s3_delete() -> None:
    storage = _build_storage()
    storage._delete_from_s3 = AsyncMock()  # type: ignore[method-assign]

    await storage.delete_file("key.png")

    storage._delete_from_s3.assert_awaited_once_with("key.png")


@pytest.mark.asyncio
async def test_upload_to_s3_raises_upload_error_on_client_error() -> None:
    storage = _build_storage()
    file = _build_upload_file()
    client = AsyncMock()
    client.put_object.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "upload failed"}},
        "PutObject",
    )
    client_context = AsyncMock()
    client_context.__aenter__.return_value = client
    client_context.__aexit__.return_value = None

    with patch.object(storage, "_get_client", return_value=client_context):
        with pytest.raises(StorageError, match="Failed to upload file"):
            await storage._upload_to_s3(file, "key.png")


@pytest.mark.asyncio
async def test_delete_from_s3_raises_delete_error_on_client_error() -> None:
    storage = _build_storage()
    client = AsyncMock()
    client.delete_object.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "delete failed"}},
        "DeleteObject",
    )
    client_context = AsyncMock()
    client_context.__aenter__.return_value = client
    client_context.__aexit__.return_value = None

    with patch.object(storage, "_get_client", return_value=client_context):
        with pytest.raises(StorageUnavailableError, match="Failed to delete file"):
            await storage._delete_from_s3("key.png")
