from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    name: str
    emoji: str = "💳"
    opening_balance: Decimal = Decimal("0")
    is_active: bool = True
    sort_order: int = 0


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    emoji: Optional[str] = None
    opening_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    emoji: str
    opening_balance: Decimal
    is_active: bool
    sort_order: int
    created_at: datetime
    current_balance: Decimal = Decimal("0")
