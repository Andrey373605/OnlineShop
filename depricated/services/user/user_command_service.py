from shop.app.application.interfaces.repositories import UnitOfWork


class UserCommandService:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def create_user(self):
        async with self._uow as uow:
            uow.users.create()

    async def update_user(self):
        pass

    async def delete_user(self):
        pass
