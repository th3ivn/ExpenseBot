import asyncio
import logging
import re
import time
from collections import defaultdict
from datetime import datetime

from aiohttp import web
from aiogram import Bot

from bot.database.transactions import save_transaction
from bot.keyboards.main import get_delete_transaction_keyboard

logger = logging.getLogger(__name__)

_rate_limit: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 10  # max requests
_RATE_LIMIT_WINDOW = 60  # seconds

UA_MONTHS = {
    "січ.": 1, "січня": 1,
    "лют.": 2, "лютого": 2,
    "бер.": 3, "березня": 3,
    "квіт.": 4, "квітня": 4,
    "трав.": 5, "травня": 5,
    "черв.": 6, "червня": 6,
    "лип.": 7, "липня": 7,
    "серп.": 8, "серпня": 8,
    "вер.": 9, "вересня": 9,
    "жовт.": 10, "жовтня": 10,
    "лист.": 11, "листопада": 11,
    "груд.": 12, "грудня": 12,
}

_UA_MONTH_PATTERN = "|".join(re.escape(k) for k in UA_MONTHS)
_UA_DATE_RE = re.compile(
    rf"(\d{{1,2}})\s+({_UA_MONTH_PATTERN})\s+(\d{{4}})\s*р?\.,?\s*(\d{{1,2}}):(\d{{2}})"
)

_EN_FORMATS = [
    "%b %d, %Y, %I:%M %p",
    "%B %d, %Y, %I:%M %p",
    "%b %d, %Y at %I:%M %p",
    "%B %d, %Y at %I:%M %p",
]


def parse_transaction_date(date_str: str) -> datetime:
    # Normalise unicode spaces
    date_str = date_str.replace("\u202f", " ").replace("\u00a0", " ")

    # 1. Try ISO format first
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass

    # 2. Try Ukrainian format
    m = _UA_DATE_RE.search(date_str)
    if m:
        day, month_str, year, hour, minute = m.groups()
        month_num = UA_MONTHS.get(month_str)
        if month_num is not None:
            try:
                return datetime(int(year), month_num, int(day), int(hour), int(minute))
            except ValueError:
                pass

    # 3. Try English formats
    for fmt in _EN_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date string: {date_str!r}")


def create_webhook_app(bot: Bot, allowed_user_id: int, webhook_secret: str) -> web.Application:
    app = web.Application()

    async def handle_health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def handle_transaction(request: web.Request) -> web.Response:
        # Rate limiting
        client_ip = request.remote or "unknown"
        now_ts = time.time()
        _rate_limit[client_ip] = [
            t for t in _rate_limit[client_ip] if now_ts - t < _RATE_LIMIT_WINDOW
        ]
        if len(_rate_limit[client_ip]) >= _RATE_LIMIT_MAX:
            logger.warning("Rate limit exceeded for %s", client_ip)
            return web.json_response({"error": "Rate limit exceeded"}, status=429)
        _rate_limit[client_ip].append(now_ts)

        data: dict = {}
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        logger.debug("Received transaction data: %s", data)

        token = data.get("token", "")
        if token != webhook_secret:
            logger.warning("Received request with invalid token")
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            amount = float(data["amount"])
            if amount <= 0:
                return web.json_response({"error": "Amount must be positive"}, status=400)
            merchant = str(data["merchant"])
            date_str = str(data["date"])
            transaction_date = parse_transaction_date(date_str)
            # Ensure naive datetime for consistency with DB TIMESTAMP columns
            if transaction_date.tzinfo is not None:
                transaction_date = transaction_date.replace(tzinfo=None)
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Invalid transaction data: %s | raw data: %s", exc, data)
            return web.json_response({"error": f"Invalid data: {exc}"}, status=400)

        tx_id = await save_transaction(
            user_id=allowed_user_id,
            amount=amount,
            merchant=merchant,
            transaction_date=transaction_date,
        )
        logger.info("Saved transaction id=%s amount=%.2f merchant=%s", tx_id, amount, merchant)

        date_formatted = transaction_date.strftime("%d.%m.%Y %H:%M")
        notification = (
            "✅ Нова транзакція!\n\n"
            f"💰 Сума: {amount:.2f} ₴\n"
            f"🏪 Продавець: {merchant}\n"
            f"📅 Дата: {date_formatted}"
        )
        for attempt in range(3):
            try:
                await bot.send_message(
                    chat_id=allowed_user_id,
                    text=notification,
                    reply_markup=get_delete_transaction_keyboard(tx_id),
                )
                break
            except Exception as exc:
                logger.error(
                    "Failed to send notification (attempt %d/3): %s", attempt + 1, exc
                )
                if attempt < 2:
                    await asyncio.sleep(1)

        return web.json_response({"ok": True, "id": tx_id})

    app.router.add_get("/", handle_health)
    app.router.add_post("/api/transaction", handle_transaction)
    return app
