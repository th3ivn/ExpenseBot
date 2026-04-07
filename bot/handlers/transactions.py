import logging
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database.transactions import (
    TRANSACTIONS_PER_PAGE,
    count_transactions,
    delete_transaction,
    get_transactions,
)
from bot.keyboards.main import (
    get_back_to_menu_keyboard,
    get_transactions_pagination_keyboard,
)
from bot.utils import safe_edit_text

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
        date_str = row["transaction_date"].strftime("%d.%m.%Y %H:%M")
        lines.append(
            f"💰 {float(row['amount']):.2f} ₴ — {row['merchant']}\n"
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
        date_str = row["transaction_date"].strftime("%d.%m")
        amount = float(row["amount"])
        total += amount
        lines.append(f"{i}. {date_str} — {row['merchant']} — {amount:.2f} ₴")

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
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    edit: bool = False,
) -> None:
    try:
        total = await count_transactions(user_id, date_from=date_from, date_to=date_to)
        total_pages = math.ceil(total / TRANSACTIONS_PER_PAGE) if total > 0 else 1
        offset = page * TRANSACTIONS_PER_PAGE

        rows = await get_transactions(
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
        else:
            await message.answer(text, reply_markup=keyboard)
    except Exception as exc:
        logger.error("Failed to load transactions: %s", exc)
        error_text = "⚠️ Помилка завантаження. Спробуйте ще раз."
        if edit:
            await safe_edit_text(message, error_text, reply_markup=get_back_to_menu_keyboard())
        else:
            await message.answer(error_text, reply_markup=get_back_to_menu_keyboard())


# ── Slash commands ────────────────────────────────────────────────────────────

@router.message(Command("transactions"))
async def cmd_transactions(message: Message) -> None:
    await _show_transactions(
        message,
        user_id=message.from_user.id,
        page=0,
        title="🧾 Останні транзакції",
        prefix="txn",
    )


@router.message(Command("week"))
async def cmd_week(message: Message) -> None:
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
        date_from=date_from,
        date_to=now,
    )


@router.message(Command("month"))
async def cmd_month(message: Message) -> None:
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_transactions(
        message,
        user_id=message.from_user.id,
        page=0,
        title="📆 Транзакції за цей місяць",
        prefix="month",
        date_from=date_from,
        date_to=now,
    )


# ── Menu callbacks ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_transactions")
async def cb_menu_transactions(callback: CallbackQuery) -> None:
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
        edit=True,
    )


@router.callback_query(F.data == "menu_week")
async def cb_menu_week(callback: CallbackQuery) -> None:
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
        date_from=date_from,
        date_to=now,
        edit=True,
    )


@router.callback_query(F.data == "menu_month")
async def cb_menu_month(callback: CallbackQuery) -> None:
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
        date_from=date_from,
        date_to=now,
        edit=True,
    )


@router.callback_query(F.data == "menu_export")
async def cb_menu_export(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        now = datetime.now(_KYIV).replace(tzinfo=None)
        date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        rows = await get_transactions(
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


# ── Pagination callbacks ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("txn_page_"))
async def cb_txn_page(callback: CallbackQuery) -> None:
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
        edit=True,
    )


@router.callback_query(F.data.startswith("week_page_"))
async def cb_week_page(callback: CallbackQuery) -> None:
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
        date_from=date_from,
        date_to=now,
        edit=True,
    )


@router.callback_query(F.data.startswith("month_page_"))
async def cb_month_page(callback: CallbackQuery) -> None:
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
        date_from=date_from,
        date_to=now,
        edit=True,
    )


# ── Delete callback ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("delete_tx_"))
async def cb_delete_transaction(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass
    try:
        tx_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await safe_edit_text(callback.message, "⚠️ Невірний ID транзакції")
        return
    try:
        deleted = await delete_transaction(tx_id, callback.from_user.id)
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
    await safe_edit_text(callback.message, text)

