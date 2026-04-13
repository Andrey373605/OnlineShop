import io
from unittest.mock import AsyncMock, Mock, patch

import pytest
from botocore.exceptions import ClientError
from fastapi import UploadFile
from starlette.datastructures import Headers

from shop.app.core.exceptions import (
    DomainValidationError,
    S3DeleteError,
    S3UploadError,
)
from shop.app.services.s3_service import S3Service


def _build_service() -> S3Service:
    return S3Service(
        endpoint_url="http://localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket_name="bucket",
        max_file_size=10,
        allowed_extensions=["png", "jpg"],
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
async def test_upload_file_success() -> None:
    service = _build_service()
    file = _build_upload_file(filename="avatar.png")
    expected_filename = "generated.png"
    service._get_filename = Mock(return_value=expected_filename)  # type: ignore[method-assign]
    service._validate_size = AsyncMock()  # type: ignore[method-assign]
    service._validate_extension = Mock()  # type: ignore[method-assign]
    service._handle_put_object = AsyncMock()  # type: ignore[method-assign]

    result = await service.upload_file(file)

    assert result == expected_filename
    service._validate_size.assert_awaited_once_with(file)
    service._validate_extension.assert_called_once_with(file)
    service._handle_put_object.assert_awaited_once_with(file, expected_filename)


@pytest.mark.asyncio
async def test_validate_size_raises_when_file_size_attr_exceeds_limit() -> None:
    service = _build_service()
    file = _build_upload_file(size=11)

    with pytest.raises(
        DomainValidationError, match="File size exceeds the allowed limit"
    ):
        await service._validate_size(file)


@pytest.mark.asyncio
async def test_validate_size_passes_when_size_from_file_object_within_limit() -> None:
    service = _build_service()
    file = _build_upload_file(size=None, data=b"1234567890")

    await service._validate_size(file)

    assert file.file.tell() == 0


@pytest.mark.asyncio
async def test_validate_size_raises_when_size_from_file_object_exceeds_limit() -> None:
    service = _build_service()
    file = _build_upload_file(size=None, data=b"12345678901")

    with pytest.raises(
        DomainValidationError, match="File size exceeds the allowed limit"
    ):
        await service._validate_size(file)


def test_validate_extension_raises_when_filename_missing_extension() -> None:
    service = _build_service()
    file = _build_upload_file(filename="filename_without_extension")

    with pytest.raises(
        DomainValidationError, match="File must have an allowed extension"
    ):
        service._validate_extension(file)


def test_validate_extension_raises_when_extension_not_allowed() -> None:
    service = _build_service()
    file = _build_upload_file(filename="document.pdf")

    with pytest.raises(DomainValidationError, match="File extension is not allowed"):
        service._validate_extension(file)


def test_get_filename_uses_generated_key_and_file_extension() -> None:
    service = _build_service()
    file = _build_upload_file(filename="photo.JPG")

    with patch.object(service, "_generate_key", return_value="abc123"):
        result = service._get_filename(file)

    assert result == "abc123.JPG"


def test_generate_key_returns_uuid_hex() -> None:
    generated = S3Service._generate_key()

    assert isinstance(generated, str)
    assert len(generated) == 32


@pytest.mark.asyncio
async def test_delete_file_raises_when_key_is_empty() -> None:
    service = _build_service()

    with pytest.raises(DomainValidationError, match="Invalid key"):
        await service.delete_file("")


@pytest.mark.asyncio
async def test_delete_file_calls_delete_handler() -> None:
    service = _build_service()
    service._handle_delete_object = AsyncMock()  # type: ignore[method-assign]

    await service.delete_file("file-key")

    service._handle_delete_object.assert_awaited_once_with("file-key")


@pytest.mark.asyncio
async def test_handle_put_object_raises_s3_upload_error_on_client_error() -> None:
    service = _build_service()
    file = _build_upload_file()
    client = AsyncMock()
    client.put_object.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "upload failed"}},
        "PutObject",
    )
    client_context = AsyncMock()
    client_context.__aenter__.return_value = client
    client_context.__aexit__.return_value = None

    with patch.object(service, "_get_client", return_value=client_context):
        with pytest.raises(S3UploadError, match="Failed to upload file"):
            await service._handle_put_object(file, "key.png")


@pytest.mark.asyncio
async def test_handle_delete_object_raises_s3_delete_error_on_client_error() -> None:
    service = _build_service()
    client = AsyncMock()
    client.delete_object.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "delete failed"}},
        "DeleteObject",
    )
    client_context = AsyncMock()
    client_context.__aenter__.return_value = client
    client_context.__aexit__.return_value = None

    with patch.object(service, "_get_client", return_value=client_context):
        with pytest.raises(S3DeleteError, match="Failed to delete file"):
            await service._handle_delete_object("key.png")
