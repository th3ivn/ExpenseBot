import pytest

from bot.keyboards.main import (
    get_back_to_menu_keyboard,
    get_delete_transaction_keyboard,
    get_main_menu_keyboard,
    get_stats_period_keyboard,
    get_transactions_pagination_keyboard,
)


# ── get_main_menu_keyboard ────────────────────────────────────────────────────

def test_main_menu_keyboard_structure():
    kb = get_main_menu_keyboard()
    # Flatten all buttons
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    callback_data_set = {btn.callback_data for btn in buttons}
    assert "menu_transactions" in callback_data_set
    assert "menu_stats" in callback_data_set
    assert "menu_week" in callback_data_set
    assert "menu_month" in callback_data_set
    assert "menu_export" in callback_data_set
    assert "menu_add_expense" in callback_data_set
    assert len(buttons) == 6


# ── get_delete_transaction_keyboard ──────────────────────────────────────────

def test_delete_transaction_keyboard_has_delete_button():
    kb = get_delete_transaction_keyboard(tx_id=7)
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    delete_btn = next(b for b in buttons if b.callback_data == "delete_tx_7")
    assert delete_btn is not None
    assert "Видалити" in delete_btn.text


def test_delete_transaction_keyboard_has_transactions_button():
    kb = get_delete_transaction_keyboard(tx_id=7)
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "menu_transactions" for b in buttons)


def test_delete_transaction_keyboard_has_menu_button():
    kb = get_delete_transaction_keyboard(tx_id=7)
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "main_menu" for b in buttons)


def test_delete_transaction_keyboard_tx_id_in_callback():
    kb = get_delete_transaction_keyboard(tx_id=99)
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "delete_tx_99" for b in buttons)


# ── get_transactions_pagination_keyboard ─────────────────────────────────────

def test_pagination_first_page_no_back():
    kb = get_transactions_pagination_keyboard(page=0, total_pages=3, prefix="txn")
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert not any("txn_page_-1" in (b.callback_data or "") for b in buttons)
    assert any(b.callback_data == "txn_page_1" for b in buttons)
    assert any(b.callback_data == "main_menu" for b in buttons)


def test_pagination_last_page_no_forward():
    kb = get_transactions_pagination_keyboard(page=2, total_pages=3, prefix="txn")
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "txn_page_1" for b in buttons)
    assert not any(b.callback_data == "txn_page_3" for b in buttons)


def test_pagination_middle_page_has_both():
    kb = get_transactions_pagination_keyboard(page=1, total_pages=3, prefix="txn")
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "txn_page_0" for b in buttons)
    assert any(b.callback_data == "txn_page_2" for b in buttons)


def test_pagination_single_page_no_nav():
    kb = get_transactions_pagination_keyboard(page=0, total_pages=1, prefix="txn")
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    nav_buttons = [b for b in buttons if b.callback_data != "main_menu"]
    assert len(nav_buttons) == 0


def test_pagination_prefix_used():
    kb = get_transactions_pagination_keyboard(page=0, total_pages=2, prefix="week")
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "week_page_1" for b in buttons)


# ── get_stats_period_keyboard ─────────────────────────────────────────────────

def test_stats_period_keyboard_has_all_periods():
    kb = get_stats_period_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    callback_data_set = {btn.callback_data for btn in buttons}
    assert "stats_week" in callback_data_set
    assert "stats_month" in callback_data_set
    assert "stats_all" in callback_data_set
    assert "main_menu" in callback_data_set


# ── get_back_to_menu_keyboard ─────────────────────────────────────────────────

def test_back_to_menu_keyboard():
    kb = get_back_to_menu_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert len(buttons) == 1
    assert buttons[0].callback_data == "main_menu"
    assert "Головне меню" in buttons[0].text
