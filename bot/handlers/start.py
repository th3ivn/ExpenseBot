import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main import get_main_menu_keyboard
from bot.utils import safe_edit_text

logger = logging.getLogger(__name__)
router = Router()
unknown_router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привіт! Я ExpenseBot — твій особистий трекер витрат.\n\n"
        "Обери дію:",
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery) -> None:
    await safe_edit_text(
        callback.message,
        "🏠 Головне меню:",
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()


@unknown_router.message()
async def unknown_message(message: Message) -> None:
    await message.answer(
        "❓ Я не розумію це повідомлення. Натисни кнопку нижче 👇",
        reply_markup=get_main_menu_keyboard(),
    )
