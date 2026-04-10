from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from bot.api_client import APIClient

_KYIV = ZoneInfo("Europe/Kyiv")


def _get_week_range() -> tuple[datetime, datetime]:
    now = datetime.now(_KYIV).replace(tzinfo=None)
    start = now - timedelta(days=now.weekday())
    date_from = start.replace(hour=0, minute=0, second=0, microsecond=0)
    date_to = now
    return date_from, date_to


def _get_month_range() -> tuple[datetime, datetime]:
    now = datetime.now(_KYIV).replace(tzinfo=None)
    date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date_to = now
    return date_from, date_to


async def get_stats_for_period(
    user_id: int,
    period: str,
    api_client: APIClient,
) -> dict:
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    if period == "week":
        date_from, date_to = _get_week_range()
    elif period == "month":
        date_from, date_to = _get_month_range()

    return await api_client.get_stats_for_period(user_id, date_from=date_from, date_to=date_to)


def format_stats_message(stats: dict, period_label: str) -> str:
    total_count = stats.get("total_count", 0)
    total_amount = float(stats.get("total_amount", 0))
    avg_amount = float(stats.get("avg_amount", 0))
    max_amount = float(stats.get("max_amount", 0))
    min_amount = float(stats.get("min_amount", 0))

    if total_count == 0:
        return f"📊 Статистика — {period_label}\n\nНемає транзакцій за цей період."

    text = (
        f"📊 Статистика — {period_label}\n\n"
        f"🔢 Кількість: {total_count}\n"
        f"💰 Загальна сума: {total_amount:.2f} ₴\n"
        f"📈 Середня: {avg_amount:.2f} ₴\n"
        f"⬆️ Макс: {max_amount:.2f} ₴\n"
        f"⬇️ Мін: {min_amount:.2f} ₴"
    )

    merchants = stats.get("top_merchants", [])
    if merchants:
        merchant_lines = "\n".join(
            f"{i}. {row['merchant']} — {float(row['total']):.2f} ₴"
            for i, row in enumerate(merchants, 1)
        )
        text += f"\n\n🏪 Топ продавців:\n{merchant_lines}"

    return text

