from abc import ABC, abstractmethod

from shop.app.models.contract.upload_source import UploadSource


class FileStorage(ABC):
    """Abstraction for operations with file storage"""

    @abstractmethod
    async def upload(self, storage_key: str, source: UploadSource) -> str:
        """Upload file and return storage key"""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete file by storage key"""
        ...
