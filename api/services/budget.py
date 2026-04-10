from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.budget import Budget
from api.models.transaction import Transaction, TransactionType
from api.schemas.budget import BudgetCreate, BudgetProgress, BudgetRead
from api.services.stats import get_budget_period


async def get_current_budget(db: AsyncSession, user_id: int) -> BudgetProgress:
    result = await db.execute(
        select(Budget)
        .where(Budget.user_id == user_id, Budget.is_active == True)  # noqa: E712
        .order_by(Budget.created_at.desc())
        .limit(1)
    )
    budget = result.scalar_one_or_none()

    period_start_day = budget.period_start_day if budget else 1
    period_start, period_end = get_budget_period(period_start_day)

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

    return BudgetProgress(
        budget=BudgetRead.model_validate(budget) if budget else None,
        period_start=period_start.date().isoformat(),
        period_end=period_end.date().isoformat(),
        distributed=distributed,
        available=available if available is not None else Decimal("0"),
    )


async def upsert_budget(db: AsyncSession, user_id: int, data: BudgetCreate) -> BudgetRead:
    result = await db.execute(
        select(Budget)
        .where(Budget.user_id == user_id, Budget.is_active == True)  # noqa: E712
        .order_by(Budget.created_at.desc())
        .limit(1)
    )
    budget = result.scalar_one_or_none()
    if budget:
        budget.amount = data.amount
        budget.period_start_day = data.period_start_day
    else:
        budget = Budget(user_id=user_id, **data.model_dump())
        db.add(budget)
    await db.flush()
    await db.refresh(budget)
    return BudgetRead.model_validate(budget)
