import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

TRANSACTIONS_PER_PAGE = 5

_MAX_RETRIES = 1
_RETRY_BASE_DELAY = 0.5
_REQUEST_TIMEOUT = 5.0

# Only idempotent HTTP methods are retried. POST is excluded because the
# server may have committed the request before the network failure, and a
# retry would create duplicate records (e.g. double-inserted transactions).
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


class APIError(Exception):
    """Raised when an API request fails. Carries a user-facing hint."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        hint: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.hint = hint or "Помилка звʼязку з сервером"


def _hint_for_status(status_code: int) -> str:
    if status_code == 401:
        return "Помилка авторизації (перевір BOT_TOKEN на API)"
    if status_code == 403:
        return "Немає доступу до ресурсу"
    if status_code == 404:
        return "Ресурс не знайдено"
    if status_code == 422:
        return "Некоректні дані запиту"
    if 500 <= status_code < 600:
        return "Внутрішня помилка сервера API"
    return f"Помилка API (HTTP {status_code})"


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

        method_upper = method.upper()
        is_idempotent = method_upper in _IDEMPOTENT_METHODS
        max_attempts = _MAX_RETRIES + 1 if is_idempotent else 1

        for attempt in range(max_attempts):
            is_last_attempt = attempt == max_attempts - 1
            try:
                async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                    response = await client.request(method, url, headers=headers, **kwargs)
            except httpx.ConnectError as exc:
                logger.error(
                    "API connect error [%s %s] attempt %d/%d: %s",
                    method, url, attempt + 1, max_attempts, exc,
                )
                if not is_last_attempt:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                raise APIError(
                    f"Cannot connect to API at {self.base_url}",
                    hint="Сервер API недоступний",
                ) from exc
            except httpx.TimeoutException as exc:
                logger.error(
                    "API timeout [%s %s] attempt %d/%d: %s",
                    method, url, attempt + 1, max_attempts, exc,
                )
                if not is_last_attempt:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                raise APIError(
                    f"API timeout on {method} {path}",
                    hint="Сервер API не відповідає",
                ) from exc
            except httpx.HTTPError as exc:
                logger.error("API transport error [%s %s]: %s", method, url, exc)
                raise APIError(
                    f"Transport error on {method} {path}",
                    hint="Помилка мережі",
                ) from exc

            if response.status_code >= 400:
                # Body preview stays in structured logs only — never in the
                # exception message — to avoid leaking PII or server stack
                # traces through log lines that re-print the exception.
                body_preview = response.text[:500] if response.text else ""
                logger.error(
                    "API error [%s %s] -> HTTP %d: %s",
                    method, url, response.status_code, body_preview,
                )

                # Retry server errors (5xx) only for idempotent methods — a
                # non-idempotent POST may have already been committed on the
                # server and retrying would duplicate the record.
                if 500 <= response.status_code < 600 and not is_last_attempt:
                    await asyncio.sleep(_RETRY_BASE_DELAY * (2 ** attempt))
                    continue

                raise APIError(
                    f"HTTP {response.status_code} on {method} {path}",
                    status_code=response.status_code,
                    hint=_hint_for_status(response.status_code),
                )

            if response.status_code == 204:
                return None

            try:
                return response.json()
            except ValueError as exc:
                # Raw body stays in logs only, not in the exception message.
                logger.error(
                    "Invalid JSON from [%s %s]: %s | body: %s",
                    method, url, exc, response.text[:500],
                )
                raise APIError(
                    f"Invalid JSON in response from {method} {path}",
                    hint="Некоректна відповідь API",
                ) from exc

        # Defensive — should never reach here.
        raise APIError("Request failed after retries", hint="Помилка запиту")

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
        except APIError as exc:
            if exc.status_code == 404:
                return False
            raise

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
