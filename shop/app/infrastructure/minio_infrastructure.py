from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from botocore.config import Config

from shop.app.core.exceptions import StorageUnavailableError
from shop.app.core.ports.base import LifecyclePort, HealthCheckPort
from shop.app.core.ports.client_provider import ClientProviderPort


class MinioInfrastructure(LifecyclePort, ClientProviderPort):
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
    ) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key

        self._config = Config(signature_version="s3v4", retries={"max_attempts": 3})

        self._client_cm = None
        self._client: AioBaseClient | None = None

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
            raise StorageUnavailableError("Failed to connect to Minio") from exc

    async def close(self) -> None:
        if self._client_cm is not None:
            await self._client_cm.__aexit__(None, None, None)
            self._client = None
            self._client_cm = None

    def get_client(self) -> AioBaseClient:
        if self._client is None:
            raise Exception("Minio client is not connected.")
        return self._client
