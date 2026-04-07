import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main import get_main_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привіт! Я ExpenseBot — твій особистий трекер витрат.\n\n"
        "Використовуй кнопки нижче для навігації:",
        reply_markup=get_main_keyboard(),
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "🏠 Головне меню:",
        reply_markup=get_main_keyboard(),
    )
    await callback.answer()
