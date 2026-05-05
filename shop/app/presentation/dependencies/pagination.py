from fastapi import Query


class CommonPaginationParams:
    def __init__(
            self,
            limit: int = Query(
                default=20,
                gt=0,
                le=100,
                description="Количество элементов на странице"
            ),
            offset: int = Query(
                default=0,
                ge=0,
                description="Количество элементов, которое нужно пропустить"
            )
    ):
        self.limit = limit
        self.offset = offset
