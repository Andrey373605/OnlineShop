from dataclasses import dataclass
from typing import BinaryIO

@dataclass
class UploadSource:
    filename: str
    content_type: str | None
    content_length: int | None
    stream: BinaryIO
    