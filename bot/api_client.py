import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, bot_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.bot_token = bot_token

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_summary(self, user_telegram_id: int) -> dict:
        return await self._request(
            "GET",
            "/api/stats/summary",
            params={"user_telegram_id": user_telegram_id},
        )

    async def get_recent_transactions(self, user_telegram_id: int, limit: int = 5) -> list:
        return await self._request(
            "GET",
            "/api/transactions",
            params={"user_telegram_id": user_telegram_id, "limit": limit},
        )

    async def create_transaction(self, user_telegram_id: int, data: dict) -> dict:
        return await self._request(
            "POST",
            "/api/transactions",
            json={**data, "user_telegram_id": user_telegram_id},
        )

    async def delete_transaction(self, user_telegram_id: int, transaction_id: int) -> bool:
        try:
            await self._request(
                "DELETE",
                f"/api/transactions/{transaction_id}",
                params={"user_telegram_id": user_telegram_id},
            )
            return True
        except httpx.HTTPStatusError as exc:
            logger.warning("Failed to delete transaction %d: %s", transaction_id, exc)
            return False
