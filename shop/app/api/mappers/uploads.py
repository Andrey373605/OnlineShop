from fastapi import UploadFile

from shop.app.models.domain.upload_source import UploadSource


def map_upload_file(file: UploadFile, content_length: int | None = None) -> UploadSource:
    return UploadSource(
        filename=file.filename or "",
        content_type=file.content_type,
        content_length=content_length,
        stream=file.file,
    )
