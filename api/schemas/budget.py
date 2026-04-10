from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class BudgetCreate(BaseModel):
    amount: Decimal
    period_start_day: int = 1

    @field_validator("period_start_day")
    @classmethod
    def validate_day(cls, v: int) -> int:
        if not 1 <= v <= 28:
            raise ValueError("День початку бюджетного періоду має бути від 1 до 28")
        return v

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Бюджет повинен бути більше нуля")
        return v


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    amount: Decimal
    period_start_day: int
    is_active: bool


class BudgetProgress(BaseModel):
    budget: Optional[BudgetRead]
    period_start: str
    period_end: str
    distributed: Decimal
    available: Decimal
