"""Placeholder repository wired into SqlUnitOfWork until a domain adapter exists."""


class UnimplementedPort:
    """Any awaited method raises NotImplementedError with a clear port name."""

    def __init__(self, port_name: str) -> None:
        self._port_name = port_name

    def __getattr__(self, name: str):
        async def _missing(*args, **kwargs):
            raise NotImplementedError(
                f"{self._port_name}.{name} is not wired to persistence yet",
            )

        return _missing
