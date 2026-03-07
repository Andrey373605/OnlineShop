from pydantic import BaseModel


class StatsOut(BaseModel):
    """Результат аналитического запроса: агрегаты по заказам, пользователям, товарам."""

    total_orders: int
    total_users: int
    total_products: int
