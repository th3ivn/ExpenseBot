from datetime import datetime

import pytest

from bot.keyboards.main import (
    get_after_save_keyboard,
    get_confirmation_keyboard,
    get_date_choice_keyboard,
)


# ── get_date_choice_keyboard ──────────────────────────────────────────────────

def test_date_choice_keyboard_button_count():
    kb = get_date_choice_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert len(buttons) == 3


def test_date_choice_keyboard_has_now():
    kb = get_date_choice_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "add_date_now" for b in buttons)


def test_date_choice_keyboard_has_custom():
    kb = get_date_choice_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "add_date_custom" for b in buttons)


def test_date_choice_keyboard_has_cancel():
    kb = get_date_choice_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "add_cancel" for b in buttons)


# ── get_confirmation_keyboard ─────────────────────────────────────────────────

def test_confirmation_keyboard_button_count():
    kb = get_confirmation_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert len(buttons) == 2


def test_confirmation_keyboard_has_confirm():
    kb = get_confirmation_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "add_confirm" for b in buttons)


def test_confirmation_keyboard_has_cancel():
    kb = get_confirmation_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "add_cancel" for b in buttons)


# ── get_after_save_keyboard ───────────────────────────────────────────────────

def test_after_save_keyboard_button_count():
    kb = get_after_save_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert len(buttons) == 2


def test_after_save_keyboard_has_transactions():
    kb = get_after_save_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "menu_transactions" for b in buttons)


def test_after_save_keyboard_has_menu():
    kb = get_after_save_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    assert any(b.callback_data == "main_menu" for b in buttons)


# ── Amount parsing ────────────────────────────────────────────────────────────

def _parse_amount(text: str) -> float | None:
    """Mirror of the parsing logic used in the handler."""
    try:
        amount = float(text.strip())
        if amount <= 0:
            raise ValueError("non-positive")
        return amount
    except (ValueError, AttributeError):
        return None


def test_parse_amount_valid_integer():
    assert _parse_amount("150") == 150.0


def test_parse_amount_valid_float():
    assert _parse_amount("150.50") == 150.50


def test_parse_amount_valid_with_spaces():
    assert _parse_amount("  200  ") == 200.0


def test_parse_amount_zero_returns_none():
    assert _parse_amount("0") is None


def test_parse_amount_negative_returns_none():
    assert _parse_amount("-50") is None


def test_parse_amount_text_returns_none():
    assert _parse_amount("abc") is None


def test_parse_amount_empty_returns_none():
    assert _parse_amount("") is None


# ── Date parsing ──────────────────────────────────────────────────────────────

def _parse_date(text: str) -> datetime | None:
    """Mirror of the parsing logic used in the handler."""
    try:
        return datetime.strptime(text.strip(), "%d.%m.%Y %H:%M")
    except (ValueError, AttributeError):
        return None


def test_parse_date_valid():
    result = _parse_date("10.04.2026 14:30")
    assert result == datetime(2026, 4, 10, 14, 30)


def test_parse_date_valid_with_spaces():
    result = _parse_date("  01.01.2025 00:00  ")
    assert result == datetime(2025, 1, 1, 0, 0)


def test_parse_date_wrong_format_returns_none():
    assert _parse_date("2026-04-10 14:30") is None


def test_parse_date_missing_time_returns_none():
    assert _parse_date("10.04.2026") is None


def test_parse_date_invalid_day_returns_none():
    assert _parse_date("32.01.2026 10:00") is None


def test_parse_date_empty_returns_none():
    assert _parse_date("") is None


def test_parse_date_text_returns_none():
    assert _parse_date("сьогодні") is None
