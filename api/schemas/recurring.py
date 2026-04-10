from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from api.models.recurring import RecurringFrequency
from api.models.transaction import TransactionType


class RecurringCreate(BaseModel):
    type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    category_id: Optional[int] = None
    account_id: int
    to_account_id: Optional[int] = None
    frequency: RecurringFrequency
    next_date: datetime
    is_active: bool = True

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Сума повинна бути більше нуля")
        return v


class RecurringUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    frequency: Optional[RecurringFrequency] = None
    next_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class RecurringRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: str
    amount: Decimal
    description: Optional[str]
    category_id: Optional[int]
    account_id: int
    to_account_id: Optional[int]
    frequency: RecurringFrequency
    next_date: datetime
    is_active: bool
    created_at: datetime
