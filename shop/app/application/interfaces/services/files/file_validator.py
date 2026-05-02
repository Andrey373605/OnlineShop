from abc import ABC, abstractmethod


class FileValidator(ABC):
    """Abstraction for validate file"""

    @abstractmethod
    def validate(self, source: UploadSource) -> None:
        """Validate the file and throwing DomainValidatorError on error"""
        ...
