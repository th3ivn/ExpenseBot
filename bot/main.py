import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery, Update

from bot.config import load_config
from bot.database.pool import close_pool, create_pool
from bot.handlers import start, transactions, stats
from bot.webhook.server import create_webhook_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class AllowedUserFilter(Filter):
    def __init__(self, allowed_user_id: int) -> None:
        self.allowed_user_id = allowed_user_id

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        if isinstance(event, Message):
            return event.from_user is not None and event.from_user.id == self.allowed_user_id
        if isinstance(event, CallbackQuery):
            return event.from_user is not None and event.from_user.id == self.allowed_user_id
        return False


async def main() -> None:
    config = load_config()

    await create_pool(config.database_url)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    allowed_filter = AllowedUserFilter(config.allowed_user_id)
    dp.message.filter(allowed_filter)
    dp.callback_query.filter(allowed_filter)

    dp.include_router(start.router)
    dp.include_router(transactions.router)
    dp.include_router(stats.router)

    webhook_app = create_webhook_app(
        bot=bot,
        allowed_user_id=config.allowed_user_id,
        webhook_secret=config.webhook_secret,
    )

    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, config.webhook_host, config.webhook_port)
    await site.start()
    logger.info("Webhook server started on %s:%s", config.webhook_host, config.webhook_port)

    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        logger.info("Shutting down...")
        await runner.cleanup()
        await close_pool()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
