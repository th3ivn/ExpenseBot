import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

from bot.state import get_last_menu_message, set_last_menu_message

logger = logging.getLogger(__name__)


async def safe_edit_text(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Edit a message, silently ignoring 'message is not modified' errors."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc).lower():
            pass  # Message not modified — ignore
        else:
            raise


async def send_or_replace(
    bot: Bot,
    chat_id: int,
    user_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message:
    """Delete the previous menu message and send a new one at the bottom of the chat."""
    old_msg_id = get_last_menu_message(user_id)
    if old_msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
        except Exception:
            pass  # Message might already be deleted

    new_msg = await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    set_last_menu_message(user_id, new_msg.message_id)
    return new_msg
