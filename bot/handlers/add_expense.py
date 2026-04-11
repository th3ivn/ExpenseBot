import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.api_client import APIClient, APIError
from bot.keyboards.main import (
    get_after_save_keyboard,
    get_back_to_menu_keyboard,
    get_confirmation_keyboard,
    get_date_choice_keyboard,
)
from bot.state import set_last_menu_message
from bot.utils import safe_edit_text, send_or_replace

logger = logging.getLogger(__name__)
router = Router()
_KYIV = ZoneInfo("Europe/Kyiv")


class AddExpenseStates(StatesGroup):
    waiting_amount = State()
    waiting_merchant = State()
    waiting_date = State()
    waiting_custom_date = State()
    confirmation = State()


def _confirmation_text(amount: float, merchant: str, date: datetime) -> str:
    date_str = date.strftime("%d.%m.%Y %H:%M")
    return (
        f"📝 Перевір дані:\n\n"
        f"💰 Сума: {amount:.2f} ₴\n"
        f"🏪 Продавець: {merchant}\n"
        f"📅 Дата: {date_str}"
    )


# ── Start flow ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_add_expense")
async def cb_menu_add_expense(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    await state.set_state(AddExpenseStates.waiting_amount)
    await safe_edit_text(
        callback.message,
        "💰 Введи суму витрати (наприклад: 150.50):",
    )
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


# ── Amount ────────────────────────────────────────────────────────────────────

@router.message(AddExpenseStates.waiting_amount)
async def msg_amount(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, AttributeError):
        await send_or_replace(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            text="⚠️ Введи коректну суму (число більше 0):",
        )
        return

    await state.update_data(amount=amount)
    await state.set_state(AddExpenseStates.waiting_merchant)
    await send_or_replace(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text="🏪 Напиши назву продавця:",
    )


# ── Merchant ──────────────────────────────────────────────────────────────────

@router.message(AddExpenseStates.waiting_merchant)
async def msg_merchant(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    merchant = (message.text or "").strip()
    if not merchant:
        await send_or_replace(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            text="⚠️ Назва продавця не може бути порожньою. Напиши назву продавця:",
        )
        return

    if len(merchant) > 255:
        merchant = merchant[:255]

    await state.update_data(merchant=merchant)
    await state.set_state(AddExpenseStates.waiting_date)
    await send_or_replace(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text="📅 Оберіть дату транзакції:",
        reply_markup=get_date_choice_keyboard(),
    )


# ── Date choice ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "add_date_now", AddExpenseStates.waiting_date)
async def cb_date_now(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    now = datetime.now(_KYIV).replace(tzinfo=None)
    await state.update_data(date=now)
    await state.set_state(AddExpenseStates.confirmation)

    data = await state.get_data()
    text = _confirmation_text(data["amount"], data["merchant"], now)
    await safe_edit_text(callback.message, text, reply_markup=get_confirmation_keyboard())
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == "add_date_custom", AddExpenseStates.waiting_date)
async def cb_date_custom(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    await state.set_state(AddExpenseStates.waiting_custom_date)
    await safe_edit_text(
        callback.message,
        "📅 Введи дату у форматі ДД.ММ.РРРР ГГ:ХХ\n(наприклад: 10.04.2026 14:30):",
    )
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


# ── Custom date input ─────────────────────────────────────────────────────────

@router.message(AddExpenseStates.waiting_custom_date)
async def msg_custom_date(message: Message, state: FSMContext) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    try:
        date = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
    except (ValueError, AttributeError):
        await send_or_replace(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            text="⚠️ Невірний формат дати. Введи у форматі ДД.ММ.РРРР ГГ:ХХ\n(наприклад: 10.04.2026 14:30):",
        )
        return

    await state.update_data(date=date)
    await state.set_state(AddExpenseStates.confirmation)

    data = await state.get_data()
    text = _confirmation_text(data["amount"], data["merchant"], date)
    await send_or_replace(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text=text,
        reply_markup=get_confirmation_keyboard(),
    )


# ── Confirm / Cancel ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "add_confirm", AddExpenseStates.confirmation)
async def cb_add_confirm(callback: CallbackQuery, state: FSMContext, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass

    data = await state.get_data()
    amount: float = data["amount"]
    merchant: str = data["merchant"]
    date: datetime = data["date"]

    try:
        await api_client.create_transaction(
            telegram_user_id=callback.from_user.id,
            amount=amount,
            merchant=merchant,
            transaction_date=date,
        )
    except APIError as exc:
        logger.error("Failed to save transaction (API error): %s", exc)
        await safe_edit_text(
            callback.message,
            f"⚠️ {exc.hint}.\nСпробуйте ще раз.",
            reply_markup=get_confirmation_keyboard(),
        )
        return
    except Exception:
        logger.exception("Unexpected error while saving transaction")
        await safe_edit_text(
            callback.message,
            "⚠️ Неочікувана помилка. Спробуйте ще раз.",
            reply_markup=get_confirmation_keyboard(),
        )
        return

    await state.clear()

    date_str = date.strftime("%d.%m.%Y %H:%M")
    success_text = (
        f"✅ Витрату додано!\n\n"
        f"💰 {amount:.2f} ₴ — {merchant}\n"
        f"📅 {date_str}"
    )
    await safe_edit_text(callback.message, success_text, reply_markup=get_after_save_keyboard())
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == "add_cancel")
async def cb_add_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    await state.clear()
    await safe_edit_text(
        callback.message,
        "❌ Скасовано",
        reply_markup=get_back_to_menu_keyboard(),
    )
    set_last_menu_message(callback.from_user.id, callback.message.message_id)
