from dataclasses import dataclass

from shop.app.core.exceptions import DomainValidationError
from shop.app.models.domain.upload_source import UploadSource


@dataclass(frozen=True)
class FileValidationRules:
    max_size_bytes: int
    allowed_extensions: set[str]


class FileValidator:
    def __init__(self, rules: FileValidationRules):
        self._rules = rules

    def validate(self, source: UploadSource) -> None:
        self._validate_size(source)
        self._validate_extension(source)

    def _validate_size(self, source: UploadSource) -> None:
        if source.content_length is not None and source.content_length > self._rules.max_size_bytes:
            raise DomainValidationError(
                f"File too large ({source.content_length} bytes). Limit: {self._rules.max_size_bytes}"
            )

        if source.content_length is not None and source.content_length > self._rules.max_size_bytes:
            raise DomainValidationError(f"File too large ({source.content_length} bytes).")

    def _validate_extension(self, source: UploadSource) -> None:
        if not source.filename or "." not in source.filename:
            raise DomainValidationError("File must have an allowed extension")

        file_ext = source.filename.rsplit(".", 1)[-1].lower().strip()

        if not file_ext:
            raise DomainValidationError("File extension is required")
        if file_ext not in self._rules.allowed_extensions:
            raise DomainValidationError("File extension is not allowed")
