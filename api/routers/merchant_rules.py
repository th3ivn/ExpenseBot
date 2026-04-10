from fastapi import APIRouter
from sqlalchemy import select

from api.dependencies import CurrentUser, DbSession
from api.models.merchant_rule import MerchantRule
from api.schemas.category import CategoryRead
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/merchant-rules", tags=["merchant-rules"])


class MerchantRuleCreate(BaseModel):
    merchant_pattern: str
    category_id: int


class MerchantRuleRead(BaseModel):
    id: int
    user_id: int
    merchant_pattern: str
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[MerchantRuleRead])
async def read_all(db: DbSession, user: CurrentUser) -> list[MerchantRuleRead]:
    result = await db.execute(
        select(MerchantRule)
        .where(MerchantRule.user_id == user.id)
        .order_by(MerchantRule.merchant_pattern)
    )
    return [MerchantRuleRead.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=MerchantRuleRead, status_code=201)
async def create(db: DbSession, user: CurrentUser, body: MerchantRuleCreate) -> MerchantRuleRead:
    rule = MerchantRule(user_id=user.id, **body.model_dump())
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return MerchantRuleRead.model_validate(rule)


@router.delete("/{rule_id}", status_code=204)
async def delete(db: DbSession, user: CurrentUser, rule_id: int) -> None:
    result = await db.execute(
        select(MerchantRule).where(MerchantRule.id == rule_id, MerchantRule.user_id == user.id)
    )
    rule = result.scalar_one_or_none()
    if rule is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Правило не знайдено")
    await db.delete(rule)
