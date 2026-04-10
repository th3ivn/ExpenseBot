import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.api_client import APIClient
from bot.keyboards.main import get_stats_period_keyboard
from bot.services.stats import format_stats_message, get_stats_for_period
from bot.state import set_last_menu_message
from bot.utils import safe_edit_text, send_or_replace

logger = logging.getLogger(__name__)
router = Router()

PERIOD_LABELS = {
    "week": "Цей тиждень",
    "month": "Цей місяць",
    "all": "Весь час",
}


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    await send_or_replace(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text="📊 Оберіть період для статистики:",
        reply_markup=get_stats_period_keyboard(),
    )


@router.callback_query(F.data == "menu_stats")
async def cb_menu_stats(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    await safe_edit_text(
        callback.message,
        "📊 Оберіть період для статистики:",
        reply_markup=get_stats_period_keyboard(),
    )
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data.in_({"stats_week", "stats_month", "stats_all"}))
async def cb_stats_period(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    period = callback.data.replace("stats_", "")
    label = PERIOD_LABELS.get(period, "")

    try:
        stats = await get_stats_for_period(callback.from_user.id, period, api_client)
        text = format_stats_message(stats, label)
    except Exception as exc:
        logger.error("Failed to load stats: %s", exc)
        text = "⚠️ Помилка завантаження статистики. Спробуйте ще раз."

    await safe_edit_text(callback.message, text, reply_markup=get_stats_period_keyboard())
    set_last_menu_message(callback.from_user.id, callback.message.message_id)
