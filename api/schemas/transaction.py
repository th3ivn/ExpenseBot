from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from api.models.transaction import TransactionType


class TagRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str


class CategoryRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    emoji: str
    color: str
    group_name: Optional[str] = None


class AccountRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    emoji: str


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    account_id: int
    to_account_id: Optional[int] = None
    date: datetime
    tag_ids: list[int] = []

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Сума повинна бути більше нуля")
        return v


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    date: Optional[datetime] = None
    tag_ids: Optional[list[int]] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Сума повинна бути більше нуля")
        return v


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TransactionType
    amount: Decimal
    description: Optional[str]
    merchant: Optional[str]
    category_id: Optional[int]
    account_id: int
    to_account_id: Optional[int]
    date: datetime
    created_at: datetime
    tags: list[TagRef] = []
    category: Optional[CategoryRef] = None
    account: Optional[AccountRef] = None
    to_account: Optional[AccountRef] = None
