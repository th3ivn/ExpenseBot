from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧾 Транзакції", callback_data="menu_transactions"),
                InlineKeyboardButton(text="📊 Статистика", callback_data="menu_stats"),
            ],
            [
                InlineKeyboardButton(text="📅 Цей тиждень", callback_data="menu_week"),
                InlineKeyboardButton(text="📆 Цей місяць", callback_data="menu_month"),
            ],
            [
                InlineKeyboardButton(text="📋 Експорт за місяць", callback_data="menu_export"),
            ],
        ]
    )


def get_delete_transaction_keyboard(tx_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ Видалити", callback_data=f"delete_tx_{tx_id}")]
        ]
    )


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu")],
        ]
    )


def get_transactions_pagination_keyboard(
    page: int,
    total_pages: int,
    prefix: str = "txn",
) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    nav_row: list[InlineKeyboardButton] = []

    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"{prefix}_page_{page - 1}")
        )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="Вперед ▶️", callback_data=f"{prefix}_page_{page + 1}")
        )

    if nav_row:
        buttons.append(nav_row)

    buttons.append(
        [InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_stats_period_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Тиждень", callback_data="stats_week"),
                InlineKeyboardButton(text="Місяць", callback_data="stats_month"),
                InlineKeyboardButton(text="Весь час", callback_data="stats_all"),
            ],
            [InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu")],
        ]
    )
