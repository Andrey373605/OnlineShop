from typing import Protocol, runtime_checkable

from shop.app.models.domain.upload_source import UploadSource


@runtime_checkable
class StoragePort(Protocol):
    """Abstraction for operations with file storage"""

    async def upload(self, source: UploadSource) -> str:
        """Upload file and return storage key"""
        ...

    async def delete(self, key: str) -> None:
        """Delete file by storage key"""
        ...


@runtime_checkable
class FileValidatorPort(Protocol):
    """Abstraction for validate file"""

    def validate(self, source: UploadSource) -> None:
        """Validate the file and throwing DomainValidatorError on error"""
        ...


@runtime_checkable
class ObjectKeyGeneratorPort(Protocol):
    """Abstraction for generating filename"""

    def generate(self, source: UploadSource) -> str:
        """Generate unique key for file"""
        ...
