from datetime import datetime
from typing import Optional

import asyncpg

from bot.database.pool import get_pool

TRANSACTIONS_PER_PAGE = 5


async def save_transaction(
    user_id: int,
    amount: float,
    merchant: str,
    transaction_date: datetime,
) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO transactions (user_id, amount, merchant, transaction_date)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            user_id,
            amount,
            merchant,
            transaction_date,
        )
    return row["id"]


async def delete_transaction(transaction_id: int, user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM transactions WHERE id = $1 AND user_id = $2",
            transaction_id,
            user_id,
        )
    return result == "DELETE 1"


async def get_transactions(
    user_id: int,
    limit: int = TRANSACTIONS_PER_PAGE,
    offset: int = 0,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if date_from and date_to:
            rows = await conn.fetch(
                """
                SELECT id, amount, merchant, transaction_date
                FROM transactions
                WHERE user_id = $1
                  AND transaction_date >= $2
                  AND transaction_date <= $3
                ORDER BY transaction_date DESC
                LIMIT $4 OFFSET $5
                """,
                user_id,
                date_from,
                date_to,
                limit,
                offset,
            )
        else:
            rows = await conn.fetch(
                """
                SELECT id, amount, merchant, transaction_date
                FROM transactions
                WHERE user_id = $1
                ORDER BY transaction_date DESC
                LIMIT $2 OFFSET $3
                """,
                user_id,
                limit,
                offset,
            )
    return rows


async def count_transactions(
    user_id: int,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if date_from and date_to:
            row = await conn.fetchrow(
                """
                SELECT COUNT(*) AS cnt
                FROM transactions
                WHERE user_id = $1
                  AND transaction_date >= $2
                  AND transaction_date <= $3
                """,
                user_id,
                date_from,
                date_to,
            )
        else:
            row = await conn.fetchrow(
                "SELECT COUNT(*) AS cnt FROM transactions WHERE user_id = $1",
                user_id,
            )
    return row["cnt"]


async def get_stats(
    user_id: int,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if date_from and date_to:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) AS total_count,
                    COALESCE(SUM(amount), 0) AS total_amount,
                    COALESCE(AVG(amount), 0) AS avg_amount,
                    COALESCE(MAX(amount), 0) AS max_amount,
                    COALESCE(MIN(amount), 0) AS min_amount
                FROM transactions
                WHERE user_id = $1
                  AND transaction_date >= $2
                  AND transaction_date <= $3
                """,
                user_id,
                date_from,
                date_to,
            )
        else:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) AS total_count,
                    COALESCE(SUM(amount), 0) AS total_amount,
                    COALESCE(AVG(amount), 0) AS avg_amount,
                    COALESCE(MAX(amount), 0) AS max_amount,
                    COALESCE(MIN(amount), 0) AS min_amount
                FROM transactions
                WHERE user_id = $1
                """,
                user_id,
            )
    return dict(row)


async def get_top_merchants(
    user_id: int,
    limit: int = 5,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[asyncpg.Record]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if date_from and date_to:
            rows = await conn.fetch(
                """
                SELECT merchant, SUM(amount) AS total
                FROM transactions
                WHERE user_id = $1
                  AND transaction_date >= $2
                  AND transaction_date <= $3
                GROUP BY merchant
                ORDER BY total DESC
                LIMIT $4
                """,
                user_id,
                date_from,
                date_to,
                limit,
            )
        else:
            rows = await conn.fetch(
                """
                SELECT merchant, SUM(amount) AS total
                FROM transactions
                WHERE user_id = $1
                GROUP BY merchant
                ORDER BY total DESC
                LIMIT $2
                """,
                user_id,
                limit,
            )
    return rows
