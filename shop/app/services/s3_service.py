import os
import uuid
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from shop.app.core.exceptions import DomainValidationError, S3DeleteError, S3UploadError


class S3Service:
    """Сервис работы с S3-совместимым хранилищем (MinIO)."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        max_file_size: int,
        allowed_extensions: list[str],
    ) -> None:
        self._endpoint_url = endpoint_url
        self._bucket_name = bucket_name
        self._max_file_size = max_file_size
        self._allowed_extensions = allowed_extensions
        self._session = get_session()
        self._config = {
            "endpoint_url": endpoint_url,
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
        }

    @asynccontextmanager
    async def _get_client(self):
        async with self._session.create_client("s3", **self._config) as client:
            yield client

    async def upload_file(self, file: UploadFile):
        await self._validate_size(file)
        self._validate_extension(file)
        filename = self._get_filename(file)
        await self._handle_put_object(file, filename)
        return filename

    async def _handle_put_object(self, file: UploadFile, filename: str):
        async with self._get_client() as client:
            try:
                await client.put_object(
                    Body=file.file,
                    Bucket=self._bucket_name,
                    Key=filename,
                    ContentType=file.content_type,
                )
            except ClientError as exc:
                raise S3UploadError("Failed to upload file") from exc

    async def delete_file(self, key: str):
        if not key:
            raise DomainValidationError("Invalid key")
        await self._handle_delete_object(key)

    async def _handle_delete_object(self, key: str):
        async with self._get_client() as client:
            try:
                return await client.delete_object(Bucket=self._bucket_name, Key=key)
            except ClientError as exc:
                raise S3DeleteError("Failed to delete file") from exc

    @staticmethod
    def _generate_key():
        return uuid.uuid4().hex

    def _get_filename(self, file: UploadFile) -> str:
        file_ext = file.filename.split(".")[-1]
        return f"{self._generate_key()}.{file_ext}"

    async def _validate_size(self, file: UploadFile) -> None:
        if file.size is not None:
            if file.size > self._max_file_size:
                raise DomainValidationError("File size exceeds the allowed limit")
            return

        def _get_file_size(f) -> int:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
            return size

        size = await run_in_threadpool(_get_file_size, file.file)
        if size > self._max_file_size:
            raise DomainValidationError("File size exceeds the allowed limit")

    def _validate_extension(self, file: UploadFile) -> None:
        if not file.filename or "." not in file.filename:
            raise DomainValidationError("File must have an allowed extension")
        file_ext = file.filename.rsplit(".", 1)[1].lower()
        if file_ext not in self._allowed_extensions:
            raise DomainValidationError("File extension is not allowed")
