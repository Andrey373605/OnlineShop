from typing import Protocol, runtime_checkable

from fastapi import UploadFile


@runtime_checkable
class StoragePort(Protocol):
    """Abstraction for operations with file storage"""

    async def upload_file(self, file: UploadFile, content_length: int | None = None) -> str:
        """Upload file and return file key"""
        ...

    async def delete_file(self, key: str) -> None:
        """Delete file by key"""
        ...


@runtime_checkable
class FileValidatorPort(Protocol):
    """Abstraction for validate file"""

    def validate(self, file: UploadFile, content_length: int | None) -> None:
        """Validate the file and throwing DomainValidatorError on error"""
        ...


@runtime_checkable
class FilenameGeneratorPort(Protocol):
    """Abstraction for generating filename"""

    def generate(self, file: UploadFile) -> str:
        """Generate unique key for file"""
        ...
