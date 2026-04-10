from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    emoji: str = "📦"
    color: str = "#8E8E93"
    group_name: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    emoji: Optional[str] = None
    color: Optional[str] = None
    group_name: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    emoji: str
    color: str
    group_name: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime
