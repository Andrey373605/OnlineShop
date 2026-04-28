from abc import ABC, abstractmethod

from shop.app.models.domain.upload_source import UploadSource


class FileStoragePort(ABC):
    """Abstraction for operations with file storage"""

    @abstractmethod
    async def upload(self, source: UploadSource) -> str:
        """Upload file and return storage key"""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete file by storage key"""
        ...


class FileValidatorPort(ABC):
    """Abstraction for validate file"""

    @abstractmethod
    def validate(self, source: UploadSource) -> None:
        """Validate the file and throwing DomainValidatorError on error"""
        ...


class ObjectKeyGeneratorPort(ABC):
    """Abstraction for generating filename"""

    @abstractmethod
    def generate(self, source: UploadSource) -> str:
        """Generate unique key for file"""
        ...
