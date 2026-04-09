import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main import get_main_menu_keyboard
from bot.state import set_last_menu_message
from bot.utils import safe_edit_text, send_or_replace

logger = logging.getLogger(__name__)
router = Router()
unknown_router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    await send_or_replace(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text="👋 Привіт! Я ExpenseBot — твій особистий трекер витрат.\n\nОбери дію:",
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    await safe_edit_text(
        callback.message,
        "🏠 Головне меню:",
        reply_markup=get_main_menu_keyboard(),
    )
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


@unknown_router.message()
async def unknown_message(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    await send_or_replace(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text="❓ Я не розумію це повідомлення. Натисни кнопку нижче 👇",
        reply_markup=get_main_menu_keyboard(),
    )
