from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MerchantRuleCreate(BaseModel):
    merchant_pattern: str
    category_id: int


class MerchantRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    merchant_pattern: str
    category_id: int
    created_at: datetime
