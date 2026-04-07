import logging
from datetime import datetime

from aiohttp import web
from aiogram import Bot

from bot.database.transactions import save_transaction

logger = logging.getLogger(__name__)


def create_webhook_app(bot: Bot, allowed_user_id: int, webhook_secret: str) -> web.Application:
    app = web.Application()

    async def handle_transaction(request: web.Request) -> web.Response:
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        token = data.get("token", "")
        if token != webhook_secret:
            logger.warning("Received request with invalid token")
            return web.json_response({"error": "Unauthorized"}, status=401)

        try:
            amount = float(data["amount"])
            merchant = str(data["merchant"])
            date_str = str(data["date"])
            transaction_date = datetime.fromisoformat(date_str)
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("Invalid transaction data: %s", exc)
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
            f"💰 Сума: {amount:.2f}\n"
            f"🏪 Продавець: {merchant}\n"
            f"📅 Дата: {date_formatted}"
        )
        try:
            await bot.send_message(chat_id=allowed_user_id, text=notification)
        except Exception as exc:
            logger.error("Failed to send notification: %s", exc)

        return web.json_response({"ok": True, "id": tx_id})

    app.router.add_post("/api/transaction", handle_transaction)
    return app
