from contextlib import asynccontextmanager

from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from shop.app.adapters.s3.client import create_aiobotocore_client
from shop.app.adapters.s3.filename_gen import UUIDFilenameGenerator
from shop.app.adapters.s3.validator import FileValidationRules, FileValidator
from shop.app.core.exceptions import DomainValidationError, S3DeleteError, S3UploadError
from shop.app.core.ports.storage import StoragePort


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

    async def upload_file(
        self,
        file: UploadFile,
        content_length: int | None = None,
    ) -> str:
        self._validator.validate(file, content_length)
        filename = self._filename_generator.generate(file)
        await self._upload_to_s3(file, filename)
        return filename

    async def delete_file(self, key: str) -> None:
        if not key:
            raise DomainValidationError("Invalid key")

        await self._delete_from_s3(key)

    async def _upload_to_s3(self, file: UploadFile, filename: str) -> None:
        async with self._get_client() as client:
            try:
                await client.put_object(
                    Body=file.file,
                    Bucket=self._bucket_name,
                    Key=filename,
                    ContentType=file.content_type,
                )
            except ClientError as exc:
                raise S3UploadError

    async def _delete_from_s3(self, key: str) -> None:
        async with self._get_client() as client:
            try:
                await client.delete_object(Bucket=self._bucket_name, Key=key)
            except ClientError as exc:
                raise S3DeleteError
