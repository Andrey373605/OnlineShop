from abc import ABC, abstractmethod


class FileNameGenerator(ABC):
    """Abstraction for generating filename"""

    @abstractmethod
    def generate(self, source: UploadSource) -> str:
        """Generate unique key for file"""
        ...
