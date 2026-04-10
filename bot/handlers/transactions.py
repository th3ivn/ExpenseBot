import logging
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.api_client import APIClient, TRANSACTIONS_PER_PAGE
from bot.keyboards.main import (
    get_back_to_menu_keyboard,
    get_transactions_pagination_keyboard,
)
from bot.state import set_last_menu_message
from bot.utils import safe_edit_text, send_or_replace

logger = logging.getLogger(__name__)
router = Router()

_KYIV = ZoneInfo("Europe/Kyiv")
_EXPORT_LIMIT = 1000
_MAX_MESSAGE_LENGTH = 4000  # Safe margin below Telegram's 4096-char limit

_UA_MONTHS_NOMINATIVE = {
    1: "січень", 2: "лютий", 3: "березень", 4: "квітень",
    5: "травень", 6: "червень", 7: "липень", 8: "серпень",
    9: "вересень", 10: "жовтень", 11: "листопад", 12: "грудень",
}


def _format_transactions(rows: list, page: int, total_pages: int, title: str) -> str:
    if not rows:
        return f"{title}\n\nНемає транзакцій."

    lines = [f"{title} (сторінка {page + 1}/{max(total_pages, 1)})\n"]
    for row in rows:
        date_val = row["date"]
        if isinstance(date_val, str):
            date_val = datetime.fromisoformat(date_val)
        date_str = date_val.strftime("%d.%m.%Y %H:%M")
        lines.append(
            f"💰 {float(row['amount']):.2f} ₴ — {row.get('merchant') or row.get('description') or '—'}\n"
            f"   📅 {date_str}"
        )
    return "\n\n".join(lines)


def _format_export(rows: list, now: datetime) -> str:
    month_name = _UA_MONTHS_NOMINATIVE.get(now.month, str(now.month))
    header = f"📋 Експорт за {month_name} {now.year}"

    if not rows:
        return f"{header}\n\nНемає транзакцій за цей місяць."

    lines = [header, ""]
    total = 0.0
    for i, row in enumerate(rows, 1):
        date_val = row["date"]
        if isinstance(date_val, str):
            date_val = datetime.fromisoformat(date_val)
        date_str = date_val.strftime("%d.%m")
        amount = float(row["amount"])
        total += amount
        merchant = row.get("merchant") or row.get("description") or "—"
        lines.append(f"{i}. {date_str} — {merchant} — {amount:.2f} ₴")

    footer = f"\nЗагальна сума: {total:.2f} ₴"

    text = "\n".join(lines) + "\n" + footer
    if len(text) > _MAX_MESSAGE_LENGTH:
        # Trim transaction lines until the message fits within Telegram's limit
        total_rows = len(rows)
        while len(text) > _MAX_MESSAGE_LENGTH and len(lines) > 3:
            lines.pop()
            shown = len(lines) - 2  # subtract header and empty line
            text = (
                "\n".join(lines)
                + f"\n\n... (показано {shown} з {total_rows} транзакцій)\n{footer}"
            )

    return text


async def _show_transactions(
    message: Message,
    user_id: int,
    page: int,
    title: str,
    prefix: str,
    api_client: APIClient,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    edit: bool = False,
) -> None:
    try:
        total = await api_client.count_transactions(user_id, date_from=date_from, date_to=date_to)
        total_pages = math.ceil(total / TRANSACTIONS_PER_PAGE) if total > 0 else 1
        offset = page * TRANSACTIONS_PER_PAGE

        rows = await api_client.get_transactions(
            user_id,
            limit=TRANSACTIONS_PER_PAGE,
            offset=offset,
            date_from=date_from,
            date_to=date_to,
        )

        text = _format_transactions(rows, page, total_pages, title)
        keyboard = get_transactions_pagination_keyboard(page, total_pages, prefix=prefix)

        if edit:
            await safe_edit_text(message, text, reply_markup=keyboard)
            set_last_menu_message(user_id, message.message_id)
        else:
            await send_or_replace(
                bot=message.bot,
                chat_id=message.chat.id,
                user_id=user_id,
                text=text,
                reply_markup=keyboard,
            )
    except Exception as exc:
        logger.error("Failed to load transactions: %s", exc)
        error_text = "⚠️ Помилка завантаження. Спробуйте ще раз."
        if edit:
            await safe_edit_text(message, error_text, reply_markup=get_back_to_menu_keyboard())
            set_last_menu_message(user_id, message.message_id)
        else:
            await send_or_replace(
                bot=message.bot,
                chat_id=message.chat.id,
                user_id=user_id,
                text=error_text,
                reply_markup=get_back_to_menu_keyboard(),
            )


# ── Slash commands ────────────────────────────────────────────────────────────

@router.message(Command("transactions"))
async def cmd_transactions(message: Message, api_client: APIClient) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    await _show_transactions(
        message,
        user_id=message.from_user.id,
        page=0,
        title="🧾 Останні транзакції",
        prefix="txn",
        api_client=api_client,
    )


@router.message(Command("week"))
async def cmd_week(message: Message, api_client: APIClient) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    await _show_transactions(
        message,
        user_id=message.from_user.id,
        page=0,
        title="📅 Транзакції за цей тиждень",
        prefix="week",
        api_client=api_client,
        date_from=date_from,
        date_to=now,
    )


@router.message(Command("month"))
async def cmd_month(message: Message, api_client: APIClient) -> None:
    try:
        await message.delete()
    except Exception:
        pass
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_transactions(
        message,
        user_id=message.from_user.id,
        page=0,
        title="📆 Транзакції за цей місяць",
        prefix="month",
        api_client=api_client,
        date_from=date_from,
        date_to=now,
    )


# ── Menu callbacks ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_transactions")
async def cb_menu_transactions(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=0,
        title="🧾 Останні транзакції",
        prefix="txn",
        api_client=api_client,
        edit=True,
    )


@router.callback_query(F.data == "menu_week")
async def cb_menu_week(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=0,
        title="📅 Транзакції за цей тиждень",
        prefix="week",
        api_client=api_client,
        date_from=date_from,
        date_to=now,
        edit=True,
    )


@router.callback_query(F.data == "menu_month")
async def cb_menu_month(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=0,
        title="📆 Транзакції за цей місяць",
        prefix="month",
        api_client=api_client,
        date_from=date_from,
        date_to=now,
        edit=True,
    )


@router.callback_query(F.data == "menu_export")
async def cb_menu_export(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        now = datetime.now(_KYIV).replace(tzinfo=None)
        date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        rows = await api_client.get_transactions(
            callback.from_user.id,
            limit=_EXPORT_LIMIT,
            offset=0,
            date_from=date_from,
            date_to=now,
        )
        text = _format_export(rows, now)
    except Exception as exc:
        logger.error("Failed to load export: %s", exc)
        text = "⚠️ Помилка завантаження. Спробуйте ще раз."
    await safe_edit_text(callback.message, text, reply_markup=get_back_to_menu_keyboard())
    set_last_menu_message(callback.from_user.id, callback.message.message_id)


# ── Pagination callbacks ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("txn_page_"))
async def cb_txn_page(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        page = int(callback.data.split("_")[-1])
        if page < 0:
            page = 0
    except (ValueError, IndexError):
        page = 0
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=page,
        title="🧾 Останні транзакції",
        prefix="txn",
        api_client=api_client,
        edit=True,
    )


@router.callback_query(F.data.startswith("week_page_"))
async def cb_week_page(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        page = int(callback.data.split("_")[-1])
        if page < 0:
            page = 0
    except (ValueError, IndexError):
        page = 0
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=page,
        title="📅 Транзакції за цей тиждень",
        prefix="week",
        api_client=api_client,
        date_from=date_from,
        date_to=now,
        edit=True,
    )


@router.callback_query(F.data.startswith("month_page_"))
async def cb_month_page(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        page = int(callback.data.split("_")[-1])
        if page < 0:
            page = 0
    except (ValueError, IndexError):
        page = 0
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=page,
        title="📆 Транзакції за цей місяць",
        prefix="month",
        api_client=api_client,
        date_from=date_from,
        date_to=now,
        edit=True,
    )


# ── Delete callback ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("delete_tx_"))
async def cb_delete_transaction(callback: CallbackQuery, api_client: APIClient) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        tx_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await safe_edit_text(callback.message, "⚠️ Невірний ID транзакції", reply_markup=get_back_to_menu_keyboard())
        return
    try:
        deleted = await api_client.delete_transaction(callback.from_user.id, tx_id)
    except Exception as exc:
        logger.error("Failed to delete transaction: %s", exc)
        await safe_edit_text(
            callback.message,
            "⚠️ Помилка видалення. Спробуйте ще раз.",
            reply_markup=get_back_to_menu_keyboard(),
        )
        return
    if deleted:
        text = "❌ Транзакцію видалено"
    else:
        text = "⚠️ Транзакцію не знайдено (можливо, вже видалена)"
    await safe_edit_text(callback.message, text, reply_markup=get_back_to_menu_keyboard())
    set_last_menu_message(callback.from_user.id, callback.message.message_id)

