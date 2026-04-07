import logging
import math
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database.transactions import (
    TRANSACTIONS_PER_PAGE,
    count_transactions,
    get_transactions,
)
from bot.keyboards.main import (
    get_back_to_menu_keyboard,
    get_transactions_pagination_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


def _format_transactions(rows: list, page: int, total_pages: int, title: str) -> str:
    if not rows:
        return f"{title}\n\nНемає транзакцій."

    lines = [f"{title} (сторінка {page + 1}/{max(total_pages, 1)})\n"]
    for row in rows:
        date_str = row["transaction_date"].strftime("%d.%m.%Y %H:%M")
        lines.append(
            f"💰 {float(row['amount']):.2f} — {row['merchant']}\n"
            f"   📅 {date_str}"
        )
    return "\n\n".join(lines)


async def _show_transactions(
    message: Message,
    user_id: int,
    page: int,
    title: str,
    prefix: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> None:
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

    await message.answer(text, reply_markup=keyboard)


# ── Reply keyboard buttons ────────────────────────────────────────────────────

@router.message(F.text == "🧾 Транзакції")
@router.message(Command("transactions"))
async def btn_transactions(message: Message) -> None:
    await _show_transactions(
        message,
        user_id=message.from_user.id,
        page=0,
        title="🧾 Останні транзакції",
        prefix="txn",
    )


@router.message(F.text == "📅 Цей тиждень")
@router.message(Command("week"))
async def btn_week(message: Message) -> None:
    now = datetime.now()
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


@router.message(F.text == "📆 Цей місяць")
@router.message(Command("month"))
async def btn_month(message: Message) -> None:
    now = datetime.now()
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


# ── Pagination callbacks ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("txn_page_"))
async def cb_txn_page(callback: CallbackQuery) -> None:
    page = int(callback.data.split("_")[-1])
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=page,
        title="🧾 Останні транзакції",
        prefix="txn",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("week_page_"))
async def cb_week_page(callback: CallbackQuery) -> None:
    page = int(callback.data.split("_")[-1])
    now = datetime.now()
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
    )
    await callback.answer()


@router.callback_query(F.data.startswith("month_page_"))
async def cb_month_page(callback: CallbackQuery) -> None:
    page = int(callback.data.split("_")[-1])
    now = datetime.now()
    date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    await _show_transactions(
        callback.message,
        user_id=callback.from_user.id,
        page=page,
        title="📆 Транзакції за цей місяць",
        prefix="month",
        date_from=date_from,
        date_to=now,
    )
    await callback.answer()
