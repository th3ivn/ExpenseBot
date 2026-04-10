from calendar import monthrange
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import cast, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.category import Category
from api.models.recurring import RecurringTransaction
from api.models.transaction import Transaction, TransactionType
from api.schemas.stats import (
    BreakdownResponse,
    CategoryBreakdown,
    DailyPoint,
    MonthlyRate,
    PlannedItem,
    SavingsRateResponse,
    SummaryResponse,
    TrendResponse,
)


def get_budget_period(period_start_day: int = 1) -> tuple[datetime, datetime]:
    now = datetime.utcnow()
    if now.day >= period_start_day:
        start = now.replace(day=period_start_day, hour=0, minute=0, second=0, microsecond=0)
    else:
        if now.month == 1:
            start = now.replace(year=now.year - 1, month=12, day=period_start_day, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now.replace(month=now.month - 1, day=period_start_day, hour=0, minute=0, second=0, microsecond=0)

    next_month = start.month % 12 + 1
    next_year = start.year + (1 if start.month == 12 else 0)
    end = start.replace(year=next_year, month=next_month) - timedelta(seconds=1)
    return start, end


async def get_summary(
    db: AsyncSession,
    user_id: int,
    period_start: datetime,
    period_end: datetime,
) -> SummaryResponse:
    from api.models.budget import Budget

    budget_result = await db.execute(
        select(Budget)
        .where(Budget.user_id == user_id, Budget.is_active == True)  # noqa: E712
        .order_by(Budget.created_at.desc())
        .limit(1)
    )
    budget = budget_result.scalar_one_or_none()

    spent_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            Transaction.date >= period_start,
            Transaction.date <= period_end,
        )
    )
    distributed: Decimal = spent_result.scalar_one()
    budget_amount = budget.amount if budget else None
    available = (budget_amount - distributed) if budget_amount is not None else None

    return SummaryResponse(
        period_start=period_start.date().isoformat(),
        period_end=period_end.date().isoformat(),
        budget_amount=budget_amount,
        distributed=distributed,
        available=available,
    )


async def get_trend(
    db: AsyncSession,
    user_id: int,
    period_start: datetime,
    period_end: datetime,
) -> TrendResponse:
    current_result = await db.execute(
        select(
            func.date(Transaction.date).label("day"),
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            Transaction.date >= period_start,
            Transaction.date <= period_end,
        )
        .group_by(func.date(Transaction.date))
        .order_by(func.date(Transaction.date))
    )
    current_period = [
        DailyPoint(date=str(row.day), amount=row.total)
        for row in current_result.all()
    ]

    prev_periods_total = Decimal("0")
    prev_days = 0
    for i in range(1, 4):
        delta = (period_end - period_start) + timedelta(seconds=1)
        p_end = period_start - timedelta(seconds=1)
        p_start = p_end - delta + timedelta(seconds=1)
        prev_result = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= p_start,
                Transaction.date <= p_end,
            )
        )
        prev_periods_total += prev_result.scalar_one()
        prev_days += (p_end - p_start).days + 1
        period_start = p_start

    avg_daily = (prev_periods_total / prev_days) if prev_days > 0 else Decimal("0")

    return TrendResponse(current_period=current_period, avg_daily_prev=avg_daily.quantize(Decimal("0.01")))


async def get_breakdown(
    db: AsyncSession,
    user_id: int,
    period_start: datetime,
    period_end: datetime,
) -> BreakdownResponse:
    result = await db.execute(
        select(
            Transaction.category_id,
            func.sum(Transaction.amount).label("total"),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            Transaction.date >= period_start,
            Transaction.date <= period_end,
        )
        .group_by(Transaction.category_id)
        .order_by(func.sum(Transaction.amount).desc())
    )
    rows = result.all()
    grand_total = sum(r.total for r in rows) or Decimal("0")

    items: list[CategoryBreakdown] = []
    for row in rows:
        if row.category_id is not None:
            cat_result = await db.execute(
                select(Category).where(Category.id == row.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            name = cat.name if cat else "Без категорії"
            group = cat.group_name if cat else None
            emoji = cat.emoji if cat else "📦"
            color = cat.color if cat else "#8E8E93"
        else:
            name = "Без категорії"
            group = None
            emoji = "📦"
            color = "#8E8E93"

        pct = (row.total / grand_total * 100).quantize(Decimal("0.01")) if grand_total else Decimal("0")
        items.append(
            CategoryBreakdown(
                category_id=row.category_id,
                category_name=name,
                group_name=group,
                emoji=emoji,
                color=color,
                total=row.total,
                percentage=pct,
            )
        )

    return BreakdownResponse(items=items, total=grand_total)


async def get_savings_rate(db: AsyncSession, user_id: int, year: int) -> SavingsRateResponse:
    months: list[MonthlyRate] = []
    for month in range(1, 13):
        _, last_day = monthrange(year, month)
        m_start = datetime(year, month, 1)
        m_end = datetime(year, month, last_day, 23, 59, 59)

        income_result = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.income,
                Transaction.date >= m_start,
                Transaction.date <= m_end,
            )
        )
        income: Decimal = income_result.scalar_one()

        expense_result = await db.execute(
            select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.expense,
                Transaction.date >= m_start,
                Transaction.date <= m_end,
            )
        )
        expense: Decimal = expense_result.scalar_one()

        rate = ((income - expense) / income * 100).quantize(Decimal("0.01")) if income > 0 else Decimal("0")
        months.append(
            MonthlyRate(
                month=f"{year}-{month:02d}",
                income=income,
                expenses=expense,
                savings_rate=rate,
            )
        )

    non_zero = [m for m in months if m.income > 0]
    avg_rate = (
        sum(m.savings_rate for m in non_zero) / len(non_zero)
    ).quantize(Decimal("0.01")) if non_zero else Decimal("0")

    return SavingsRateResponse(year=year, months=months, avg_savings_rate=avg_rate)


async def get_planned(db: AsyncSession, user_id: int) -> list[PlannedItem]:
    result = await db.execute(
        select(RecurringTransaction)
        .options(selectinload(RecurringTransaction.category))
        .where(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.is_active == True,  # noqa: E712
        )
        .order_by(RecurringTransaction.next_date)
    )
    items = []
    for rec in result.scalars().all():
        cat_name = rec.category.name if rec.category else None
        items.append(
            PlannedItem(
                id=rec.id,
                type=rec.type,
                amount=rec.amount,
                description=rec.description,
                category_id=rec.category_id,
                category_name=cat_name,
                frequency=rec.frequency,
                next_date=rec.next_date.date().isoformat(),
            )
        )
    return items
