from aiobotocore.client import AioBaseClient

from botocore.exceptions import ClientError, BotoCoreError

from shop.app.core.exceptions import StorageUnavailableError, StorageValidationError

from shop.app.core.ports.file_storage import FileStoragePort
from shop.app.models.domain.upload_source import UploadSource


class S3Storage(FileStoragePort):
    """File storage adapter S3-compatible client surface"""

    def __init__(self, *, client: AioBaseClient, bucket_name: str) -> None:
        self._client = client
        self._bucket_name = bucket_name

    async def upload(self, storage_key: str, source: UploadSource) -> str:
        await self._upload_to_s3(source, storage_key)
        return storage_key

    async def delete(self, key: str) -> None:
        if not key:
            raise StorageValidationError("Invalid key")
        await self._delete_from_s3(key)

    async def _upload_to_s3(self, source: UploadSource, storage_key: str) -> None:
        try:
            await self._client.put_object(
                Body=source.stream,
                Bucket=self._bucket_name,
                Key=storage_key,
                ContentType=source.content_type,
            )
        except (ClientError, BotoCoreError) as exc:
            raise StorageUnavailableError("Failed to upload object to storage") from exc

    async def _delete_from_s3(self, key: str) -> None:
        try:
            await self._client.delete_object(Bucket=self._bucket_name, Key=key)
        except (ClientError, BotoCoreError) as exc:
            raise StorageUnavailableError("Failed to delete object to storage") from exc
