class ApplicationError(Exception):
    """Base class for all application-layer errors."""

    code: str = "application_error"

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)
