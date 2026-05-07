class MediaUrlBuilder:
    def __init__(self, media_base_url: str) -> None:
        self._media_base_url = media_base_url.rstrip("/")

    def build(self, storage_key: str) -> str:
        normalized_key = storage_key.lstrip("/")
        return f"{self._media_base_url}/{normalized_key}"
