from contextlib import asynccontextmanager

from botocore.config import Config
from botocore.exceptions import ClientError

from shop.app.adapters.s3.client import create_aiobotocore_client
from shop.app.adapters.s3.filename_gen import UUIDFilenameGenerator
from shop.app.adapters.s3.validator import FileValidationRules, FileValidator
from shop.app.core.exceptions import (
    DomainValidationError,
    StorageUnavailableError,
)
from shop.app.core.ports.storage import StoragePort
from shop.app.models.domain.upload_source import UploadSource


class S3Storage(StoragePort):
    """File storage adapter S3-compatible client surface"""

    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        max_file_size: int,
        allowed_extensions: set[str],
    ) -> None:
        self._bucket_name = bucket_name
        self._validator = FileValidator(
            FileValidationRules(
                max_size_bytes=max_file_size,
                allowed_extensions=allowed_extensions,
            )
        )
        self._filename_generator = UUIDFilenameGenerator()
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._client_config = Config(signature_version="s3v4")

    @asynccontextmanager
    async def _get_client(self):
        async with create_aiobotocore_client(
            endpoint_url=self._endpoint_url,
            access_key=self._access_key,
            secret_key=self._secret_key,
            config=self._client_config,
        ) as client:
            yield client

    async def upload(self, source: UploadSource) -> str:
        self._validator.validate(source)
        storage_key = self._filename_generator.generate(source)
        await self._upload_to_s3(source, storage_key)
        return storage_key

    async def delete(self, key: str) -> None:
        if not key:
            raise DomainValidationError("Invalid key")

        await self._delete_from_s3(key)

    async def _upload_to_s3(self, source: UploadSource, storage_key: str) -> None:
        async with self._get_client() as client:
            try:
                await client.put_object(
                    Body=source.stream,
                    Bucket=self._bucket_name,
                    Key=storage_key,
                    ContentType=source.content_type,
                )
            except ClientError as exc:
                raise StorageUnavailableError("Failed to upload object to storage") from exc

    async def _delete_from_s3(self, key: str) -> None:
        async with self._get_client() as client:
            try:
                await client.delete_object(Bucket=self._bucket_name, Key=key)
            except ClientError as exc:
                raise StorageUnavailableError("Failed to delete object to storage") from exc
