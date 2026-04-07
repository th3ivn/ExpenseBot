import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main import get_stats_period_keyboard
from bot.services.stats import format_stats_message, get_stats_for_period

logger = logging.getLogger(__name__)
router = Router()

PERIOD_LABELS = {
    "week": "Цей тиждень",
    "month": "Цей місяць",
    "all": "Весь час",
}


@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def btn_stats(message: Message) -> None:
    await message.answer(
        "📊 Оберіть період для статистики:",
        reply_markup=get_stats_period_keyboard(),
    )


@router.callback_query(F.data.in_({"stats_week", "stats_month", "stats_all"}))
async def cb_stats_period(callback: CallbackQuery) -> None:
    period = callback.data.replace("stats_", "")
    label = PERIOD_LABELS.get(period, "")

    stats = await get_stats_for_period(callback.from_user.id, period)
    text = format_stats_message(stats, label)

    await callback.message.answer(text, reply_markup=get_stats_period_keyboard())
    await callback.answer()
