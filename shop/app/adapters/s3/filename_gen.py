import uuid
from collections.abc import Callable
from datetime import datetime

from shop.app.models.domain.upload_source import UploadSource
from shop.app.utils.get_utc_now import get_utc_now


class UUIDFilenameGenerator:
    def __init__(
        self,
        date_format: str = "%Y/%m/%d",
        time_provider: Callable[[], datetime] | None = None,
        uuid_provider: Callable[[], str] | None = None,
    ):
        self._date_format = date_format
        self._time_provider = time_provider or get_utc_now
        self._uuid_provider = uuid_provider or (lambda: uuid.uuid4().hex)

    def generate(self, source: UploadSource) -> str:
        file_ext = source.filename.rsplit(".")[-1].lower()
        date_prefix = self._time_provider().strftime(self._date_format)
        unique_id = self._uuid_provider()
        return f"{date_prefix}/{unique_id}.{file_ext}"
