from typing import Protocol, Any


class UseCase(Protocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
