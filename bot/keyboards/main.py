from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🧾 Транзакції"),
                KeyboardButton(text="📊 Статистика"),
            ],
            [
                KeyboardButton(text="📅 Цей тиждень"),
                KeyboardButton(text="📆 Цей місяць"),
            ],
        ],
        resize_keyboard=True,
        persistent=True,
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
