from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from api.dependencies import CurrentUser, DbSession
from api.schemas.stats import (
    BreakdownResponse,
    SavingsRateResponse,
    SummaryResponse,
    TrendResponse,
    PlannedItem,
)
from api.services.stats import (
    get_breakdown,
    get_planned,
    get_savings_rate,
    get_summary,
    get_trend,
    get_budget_period,
)

router = APIRouter(prefix="/stats", tags=["stats"])


def _resolve_period(
    period_start: Optional[datetime],
    period_end: Optional[datetime],
    user_period_start_day: int = 1,
) -> tuple[datetime, datetime]:
    if period_start and period_end:
        return period_start, period_end
    return get_budget_period(user_period_start_day)


@router.get("/summary", response_model=SummaryResponse)
async def summary(
    db: DbSession,
    user: CurrentUser,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
) -> SummaryResponse:
    start, end = _resolve_period(period_start, period_end)
    return await get_summary(db, user.id, start, end)


@router.get("/trend", response_model=TrendResponse)
async def trend(
    db: DbSession,
    user: CurrentUser,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
) -> TrendResponse:
    start, end = _resolve_period(period_start, period_end)
    return await get_trend(db, user.id, start, end)


@router.get("/breakdown", response_model=BreakdownResponse)
async def breakdown(
    db: DbSession,
    user: CurrentUser,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
) -> BreakdownResponse:
    start, end = _resolve_period(period_start, period_end)
    return await get_breakdown(db, user.id, start, end)


@router.get("/savings-rate", response_model=SavingsRateResponse)
async def savings_rate(
    db: DbSession,
    user: CurrentUser,
    year: int = Query(default=datetime.utcnow().year),
) -> SavingsRateResponse:
    return await get_savings_rate(db, user.id, year)


@router.get("/planned", response_model=list[PlannedItem])
async def planned(db: DbSession, user: CurrentUser) -> list[PlannedItem]:
    return await get_planned(db, user.id)
