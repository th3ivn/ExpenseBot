import pytest

from bot.webhook.server import parse_transaction_date


def test_iso_format():
    dt = parse_transaction_date("2024-03-15T14:30:00")
    assert dt.year == 2024
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30


def test_ua_date_short_month():
    dt = parse_transaction_date("15 бер. 2024 р., 14:30")
    assert dt.year == 2024
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30


def test_ua_date_full_month():
    dt = parse_transaction_date("15 березня 2024 р., 14:30")
    assert dt.year == 2024
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30


def test_en_date():
    dt = parse_transaction_date("Mar 15, 2024, 2:30 PM")
    assert dt.year == 2024
    assert dt.month == 3
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30


def test_unicode_spaces():
    # \u202f is narrow no-break space used by iPhone
    dt = parse_transaction_date("15 бер. 2024\u202fр.,\u202f14:30")
    assert dt.year == 2024
    assert dt.month == 3
    assert dt.day == 15


def test_invalid_date_raises_value_error():
    with pytest.raises(ValueError):
        parse_transaction_date("not a date at all")


def test_all_ua_months_short():
    months = {
        "січ.": 1, "лют.": 2, "бер.": 3, "квіт.": 4,
        "трав.": 5, "черв.": 6, "лип.": 7, "серп.": 8,
        "вер.": 9, "жовт.": 10, "лист.": 11, "груд.": 12,
    }
    for abbr, expected_month in months.items():
        dt = parse_transaction_date(f"1 {abbr} 2024 р., 10:00")
        assert dt.month == expected_month, f"Failed for {abbr}"
