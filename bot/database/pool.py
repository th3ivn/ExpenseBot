import asyncio
import logging
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def create_pool(database_url: str) -> asyncpg.Pool:
    global _pool
    for attempt in range(3):
        try:
            _pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
            await _init_db(_pool)
            logger.info("Database pool created")
            return _pool
        except Exception as exc:
            logger.error("Failed to create pool (attempt %d/3): %s", attempt + 1, exc)
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
            else:
                raise


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")


async def _init_db(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                merchant VARCHAR(255) NOT NULL,
                transaction_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);"
        )
    logger.info("Database schema initialized")
