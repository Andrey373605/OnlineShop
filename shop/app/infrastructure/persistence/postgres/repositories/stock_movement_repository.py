from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from shop.app.application.interfaces.repositories import StockMovementRepository
from shop.app.domain import StockMovement
from shop.app.domain.entities.stock_movement import MovementReason


class StockMovementRepositorySql(StockMovementRepository):
    def __init__(self, conn):
        self._conn = conn

    async def add(self, movement: StockMovement) -> None:
        await self._conn.execute(
            """
            INSERT INTO stock_movements (
                id, product_id, warehouse_id, amount, reason, created_at, product_variant_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7);
            """,
            movement.id,
            movement.product_id,
            movement.warehouse_id,
            movement.amount,
            movement.reason.value,
            movement.created_at,
            movement.product_variant_id,
        )

    async def list_by_warehouse(
        self, warehouse_id: UUID, limit: int, offset: int
    ) -> list[StockMovement]:
        rows = await self._conn.fetch(
            """
            SELECT id, product_id, warehouse_id, amount, reason, created_at, product_variant_id
            FROM stock_movements
            WHERE warehouse_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
            """,
            warehouse_id,
            limit,
            offset,
        )
        return [self._map_row(row) for row in rows]

    async def list_by_product(
        self, product_id: UUID, limit: int, offset: int
    ) -> list[StockMovement]:
        rows = await self._conn.fetch(
            """
            SELECT id, product_id, warehouse_id, amount, reason, created_at, product_variant_id
            FROM stock_movements
            WHERE product_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
            """,
            product_id,
            limit,
            offset,
        )
        return [self._map_row(row) for row in rows]

    async def list_by_variant(
        self, variant_id: UUID, limit: int, offset: int
    ) -> list[StockMovement]:
        rows = await self._conn.fetch(
            """
            SELECT id, product_id, warehouse_id, amount, reason, created_at, product_variant_id
            FROM stock_movements
            WHERE product_variant_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
            """,
            variant_id,
            limit,
            offset,
        )
        return [self._map_row(row) for row in rows]

    async def list_by_period(
        self,
        time_from: datetime,
        time_to: datetime,
        *,
        limit: int,
        offset: int,
    ) -> list[StockMovement]:
        rows = await self._conn.fetch(
            """
            SELECT id, product_id, warehouse_id, amount, reason, created_at, product_variant_id
            FROM stock_movements
            WHERE created_at >= $1 AND created_at <= $2
            ORDER BY created_at DESC
            LIMIT $3 OFFSET $4;
            """,
            time_from,
            time_to,
            limit,
            offset,
        )
        return [self._map_row(row) for row in rows]

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> StockMovement:
        return StockMovement(
            id=row["id"],
            product_id=row["product_id"],
            warehouse_id=row["warehouse_id"],
            amount=row["amount"],
            reason=MovementReason(str(row["reason"])),
            created_at=row["created_at"],
            product_variant_id=row["product_variant_id"],
        )
