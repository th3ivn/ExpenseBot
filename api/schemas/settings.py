from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class SettingsUpdate(BaseModel):
    budget_period_start_day: Optional[int] = None
    theme: Optional[str] = None

    @field_validator("budget_period_start_day")
    @classmethod
    def validate_day(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not 1 <= v <= 28:
            raise ValueError("День початку бюджетного періоду має бути від 1 до 28")
        return v


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    budget_period_start_day: int
    theme: str
    created_at: datetime
    updated_at: datetime
