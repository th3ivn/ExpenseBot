import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main import get_stats_period_keyboard
from bot.services.stats import format_stats_message, get_stats_for_period
from bot.utils import safe_edit_text

logger = logging.getLogger(__name__)
router = Router()

PERIOD_LABELS = {
    "week": "Цей тиждень",
    "month": "Цей місяць",
    "all": "Весь час",
}


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    await message.answer(
        "📊 Оберіть період для статистики:",
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


@router.callback_query(F.data.in_({"stats_week", "stats_month", "stats_all"}))
async def cb_stats_period(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    period = callback.data.replace("stats_", "")
    label = PERIOD_LABELS.get(period, "")

    try:
        stats = await get_stats_for_period(callback.from_user.id, period)
        text = format_stats_message(stats, label)
    except Exception as exc:
        logger.error("Failed to load stats: %s", exc)
        text = "⚠️ Помилка завантаження статистики. Спробуйте ще раз."

    await safe_edit_text(callback.message, text, reply_markup=get_stats_period_keyboard())
