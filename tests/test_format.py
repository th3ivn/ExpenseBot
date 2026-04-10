from datetime import datetime
from unittest.mock import MagicMock

import pytest

from bot.handlers.transactions import _format_export, _format_transactions
from bot.services.stats import format_stats_message


def _make_row(amount: float, merchant: str, date: datetime) -> MagicMock:
    row = MagicMock()
    row.__getitem__ = lambda self, key: {
        "amount": amount,
        "merchant": merchant,
        "date": date.isoformat(),
    }[key]
    row.get = lambda key, default=None: {
        "amount": amount,
        "merchant": merchant,
        "date": date.isoformat(),
    }.get(key, default)
    return row


# ── _format_transactions ──────────────────────────────────────────────────────

def test_format_transactions_with_data():
    rows = [
        _make_row(100.50, "Silpo", datetime(2024, 3, 15, 14, 30)),
        _make_row(50.00, "ATB", datetime(2024, 3, 14, 10, 0)),
    ]
    result = _format_transactions(rows, page=0, total_pages=1, title="🧾 Транзакції")
    assert "🧾 Транзакції" in result
    assert "100.50 ₴" in result
    assert "Silpo" in result
    assert "50.00 ₴" in result
    assert "ATB" in result
    assert "15.03.2024" in result


def test_format_transactions_empty():
    result = _format_transactions([], page=0, total_pages=1, title="🧾 Транзакції")
    assert "Немає транзакцій" in result
    assert "🧾 Транзакції" in result


def test_format_transactions_pagination_label():
    rows = [_make_row(10.0, "Shop", datetime(2024, 1, 1, 0, 0))]
    result = _format_transactions(rows, page=1, total_pages=3, title="🧾")
    assert "2/3" in result


# ── _format_export ────────────────────────────────────────────────────────────

def test_format_export_with_data():
    now = datetime(2024, 3, 15, 12, 0)
    rows = [
        _make_row(200.0, "McDonald's", datetime(2024, 3, 10, 12, 0)),
        _make_row(50.0, "Nova Poshta", datetime(2024, 3, 5, 9, 0)),
    ]
    result = _format_export(rows, now)
    assert "березень 2024" in result or "берез" in result.lower() or "Експорт за" in result
    assert "200.00 ₴" in result
    assert "McDonald's" in result
    assert "250.00 ₴" in result  # total


def test_format_export_empty():
    now = datetime(2024, 3, 15, 12, 0)
    result = _format_export([], now)
    assert "Немає транзакцій" in result


def test_format_export_truncation():
    now = datetime(2024, 3, 15, 12, 0)
    # Create many rows to trigger truncation
    rows = [_make_row(1.0, "A" * 80, datetime(2024, 3, i % 28 + 1, 0, 0)) for i in range(100)]
    result = _format_export(rows, now)
    assert len(result) <= 4100  # safe margin above 4000


# ── format_stats_message ──────────────────────────────────────────────────────

def test_format_stats_message_with_data():
    stats = {
        "total_count": 5,
        "total_amount": 500.0,
        "avg_amount": 100.0,
        "max_amount": 200.0,
        "min_amount": 50.0,
        "top_merchants": [
            {"merchant": "Silpo", "total": 300.0},
            {"merchant": "ATB", "total": 200.0},
        ],
    }
    result = format_stats_message(stats, "Цей місяць")
    assert "Цей місяць" in result
    assert "500.00 ₴" in result
    assert "Silpo" in result
    assert "ATB" in result


def test_format_stats_message_no_transactions():
    stats = {
        "total_count": 0,
        "total_amount": 0,
        "avg_amount": 0,
        "max_amount": 0,
        "min_amount": 0,
        "top_merchants": [],
    }
    result = format_stats_message(stats, "Весь час")
    assert "Немає транзакцій" in result
    assert "Весь час" in result
