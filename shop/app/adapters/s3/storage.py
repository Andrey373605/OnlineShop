from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

from shop.app.adapters.s3.filename_gen import UUIDFilenameGenerator
from shop.app.adapters.s3.validator import FileValidator
from shop.app.core.exceptions import StorageUnavailableError, StorageValidationError
from shop.app.core.ports.base import LifecyclePort, HealthCheckPort

from shop.app.core.ports.file_storage import FileStoragePort
from shop.app.models.domain.upload_source import UploadSource


class S3Storage(FileStoragePort, LifecyclePort, HealthCheckPort):
    """File storage adapter S3-compatible client surface"""

    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        validator: FileValidator,
        filename_generator: UUIDFilenameGenerator,
    ) -> None:
        self._bucket_name = bucket_name
        self._validator = validator
        self._filename_generator = filename_generator
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._config = Config(signature_version="s3v4")
        self._client_cm = None
        self._client: AioBaseClient | None = None

    def _get_client(self) -> AioBaseClient:
        if self._client is None:
            raise StorageUnavailableError("Storage client is not connected.")
        return self._client

    async def connect(self) -> None:
        if self._client is not None:
            return

        session = get_session()
        try:
            self._client_cm = session.create_client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                config=self._config,
            )
            self._client = await self._client_cm.__aenter__()
        except Exception as exc:
            self._client_cm = None
            self._client = None
            raise StorageUnavailableError("Failed to connect to storage") from exc

    async def close(self) -> None:
        if self._client_cm is not None:
            await self._client_cm.__aexit__(None, None, None)
            self._client = None
            self._client_cm = None

    async def ensure_ready(self) -> None:
        client = self._get_client()
        try:
            await client.head_bucket(Bucket=self._bucket_name)
        except (ClientError, BotoCoreError) as exc:
            raise StorageUnavailableError("Storage is not ready") from exc

    async def upload(self, source: UploadSource) -> str:
        self._validator.validate(source)
        storage_key = self._filename_generator.generate(source)
        await self._upload_to_s3(source, storage_key)
        return storage_key

    async def delete(self, key: str) -> None:
        if not key:
            raise StorageValidationError("Invalid key")
        await self._delete_from_s3(key)

    async def _upload_to_s3(self, source: UploadSource, storage_key: str) -> None:
        client = self._get_client()
        try:
            await client.put_object(
                Body=source.stream,
                Bucket=self._bucket_name,
                Key=storage_key,
                ContentType=source.content_type,
            )
        except (ClientError, BotoCoreError) as exc:
            raise StorageUnavailableError("Failed to upload object to storage") from exc

    async def _delete_from_s3(self, key: str) -> None:
        client = self._get_client()
        try:
            await client.delete_object(Bucket=self._bucket_name, Key=key)
        except (ClientError, BotoCoreError) as exc:
            raise StorageUnavailableError("Failed to delete object to storage") from exc
