from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    period_start: str
    period_end: str
    budget_amount: Optional[Decimal]
    distributed: Decimal
    available: Optional[Decimal]


class DailyPoint(BaseModel):
    date: str
    amount: Decimal


class TrendResponse(BaseModel):
    current_period: list[DailyPoint]
    avg_daily_prev: Decimal


class CategoryBreakdown(BaseModel):
    category_id: Optional[int]
    category_name: str
    group_name: Optional[str]
    emoji: str
    color: str
    total: Decimal
    percentage: Decimal


class BreakdownResponse(BaseModel):
    items: list[CategoryBreakdown]
    total: Decimal


class MonthlyRate(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal
    savings_rate: Decimal


class SavingsRateResponse(BaseModel):
    year: int
    months: list[MonthlyRate]
    avg_savings_rate: Decimal


class PlannedItem(BaseModel):
    id: int
    type: str
    amount: Decimal
    description: Optional[str]
    category_id: Optional[int]
    category_name: Optional[str]
    frequency: str
    next_date: str
