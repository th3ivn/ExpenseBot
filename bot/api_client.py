import logging
from datetime import datetime
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

TRANSACTIONS_PER_PAGE = 5


class APIClient:
    def __init__(self, base_url: str, bot_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.bot_token = bot_token

    async def _request(
        self,
        method: str,
        path: str,
        telegram_user_id: Optional[int] = None,
        **kwargs: Any,
    ) -> Any:
        headers: dict[str, str] = kwargs.pop("headers", {})
        headers["X-Bot-Token"] = self.bot_token
        if telegram_user_id is not None:
            headers["X-Telegram-User-Id"] = str(telegram_user_id)
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return None
            return response.json()

    async def get_default_account_id(self, telegram_user_id: int) -> int:
        accounts = await self._request("GET", "/api/accounts", telegram_user_id=telegram_user_id)
        if accounts:
            return accounts[0]["id"]
        new_account = await self._request(
            "POST",
            "/api/accounts",
            telegram_user_id=telegram_user_id,
            json={"name": "Готівка", "emoji": "💵", "opening_balance": "0"},
        )
        return new_account["id"]

    async def get_summary(self, telegram_user_id: int) -> dict:
        return await self._request(
            "GET",
            "/api/stats/summary",
            telegram_user_id=telegram_user_id,
        )

    async def get_transactions(
        self,
        telegram_user_id: int,
        limit: int = TRANSACTIONS_PER_PAGE,
        offset: int = 0,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if date_from is not None:
            params["period_start"] = date_from.isoformat()
        if date_to is not None:
            params["period_end"] = date_to.isoformat()
        return await self._request(
            "GET",
            "/api/transactions",
            telegram_user_id=telegram_user_id,
            params=params,
        )

    async def count_transactions(
        self,
        telegram_user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> int:
        params: dict[str, Any] = {}
        if date_from is not None:
            params["period_start"] = date_from.isoformat()
        if date_to is not None:
            params["period_end"] = date_to.isoformat()
        result = await self._request(
            "GET",
            "/api/transactions/count",
            telegram_user_id=telegram_user_id,
            params=params,
        )
        return result["count"]

    async def get_recent_transactions(self, telegram_user_id: int, limit: int = 5) -> list:
        return await self._request(
            "GET",
            "/api/transactions/recent",
            telegram_user_id=telegram_user_id,
            params={"n": limit},
        )

    async def create_transaction(
        self,
        telegram_user_id: int,
        amount: float,
        merchant: str,
        transaction_date: datetime,
    ) -> dict:
        account_id = await self.get_default_account_id(telegram_user_id)
        return await self._request(
            "POST",
            "/api/transactions",
            telegram_user_id=telegram_user_id,
            json={
                "type": "expense",
                "amount": str(amount),
                "merchant": merchant,
                "date": transaction_date.isoformat(),
                "account_id": account_id,
            },
        )

    async def delete_transaction(self, telegram_user_id: int, transaction_id: int) -> bool:
        try:
            await self._request(
                "DELETE",
                f"/api/transactions/{transaction_id}",
                telegram_user_id=telegram_user_id,
            )
            return True
        except httpx.HTTPStatusError as exc:
            logger.warning("Failed to delete transaction %d: %s", transaction_id, exc)
            return False

    async def get_stats_for_period(
        self,
        telegram_user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        params: dict[str, Any] = {"limit": 500, "offset": 0}
        if date_from is not None:
            params["period_start"] = date_from.isoformat()
        if date_to is not None:
            params["period_end"] = date_to.isoformat()
        rows = await self._request(
            "GET",
            "/api/transactions",
            telegram_user_id=telegram_user_id,
            params=params,
        )
        expenses = [r for r in rows if r.get("type") == "expense"]
        if not expenses:
            return {
                "total_count": 0,
                "total_amount": 0.0,
                "avg_amount": 0.0,
                "max_amount": 0.0,
                "min_amount": 0.0,
                "top_merchants": [],
            }
        amounts = [float(r["amount"]) for r in expenses]
        total_count = len(expenses)
        total_amount = sum(amounts)
        avg_amount = total_amount / total_count
        max_amount = max(amounts)
        min_amount = min(amounts)

        merchant_totals: dict[str, float] = {}
        for row in expenses:
            m = row.get("merchant") or "Невідомо"
            merchant_totals[m] = merchant_totals.get(m, 0.0) + float(row["amount"])
        top_merchants = [
            {"merchant": m, "total": t}
            for m, t in sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return {
            "total_count": total_count,
            "total_amount": total_amount,
            "avg_amount": avg_amount,
            "max_amount": max_amount,
            "min_amount": min_amount,
            "top_merchants": top_merchants,
        }
