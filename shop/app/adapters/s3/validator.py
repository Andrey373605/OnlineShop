from dataclasses import dataclass

from fastapi import UploadFile

from shop.app.core.exceptions import DomainValidationError


@dataclass(frozen=True)
class FileValidationRules:
    max_size_bytes: int
    allowed_extensions: set[str]


class FileValidator:
    def __init__(self, rules: FileValidationRules):
        self._rules = rules

    def validate(self, file: UploadFile, content_length: int | None) -> None:
        self._validate_size(file, content_length)
        self._validate_extension(file)

    def _validate_size(self, file: UploadFile, content_length: int | None) -> None:
        if content_length is not None and content_length > self._rules.max_size_bytes:
            raise DomainValidationError(
                f"File too large ({content_length} bytes). Limit: {self._rules.max_size_bytes}"
            )

        if file.size is not None and file.size > self._rules.max_size_bytes:
            raise DomainValidationError(f"File too large ({file.size} bytes).")

    def _validate_extension(self, file: UploadFile) -> None:
        if not file.filename or "." not in file.filename:
            raise DomainValidationError("File must have an allowed extension")

        file_ext = file.filename.rsplit(".", 1)[-1].lower().strip()

        if not file_ext:
            raise DomainValidationError("File extension is required")
        if file_ext not in self._rules.allowed_extensions:
            raise DomainValidationError("File extension is not allowed")
