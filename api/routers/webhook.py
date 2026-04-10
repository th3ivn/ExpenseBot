from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.config import settings
from api.database.session import get_db
from api.models.transaction import Transaction, TransactionType
from api.models.user import User
from api.services.auto_categorize import auto_categorize

router = APIRouter(prefix="/webhook", tags=["webhook"])


class WebhookTransactionPayload(BaseModel):
    telegram_id: int
    type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    merchant: Optional[str] = None
    account_id: int
    to_account_id: Optional[int] = None
    date: Optional[datetime] = None


@router.post("/transaction", status_code=201)
async def receive_transaction(
    body: WebhookTransactionPayload,
    x_webhook_secret: Optional[str] = Header(None),
) -> dict:
    if not x_webhook_secret or x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний webhook secret",
        )

    async for db in get_db():
        user_result = await db.execute(
            select(User).where(User.telegram_id == body.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Користувача не знайдено")

        category_id: Optional[int] = None
        if body.merchant:
            category_id = await auto_categorize(db, user.id, body.merchant)

        t = Transaction(
            user_id=user.id,
            type=body.type,
            amount=body.amount,
            description=body.description,
            merchant=body.merchant,
            category_id=category_id,
            account_id=body.account_id,
            to_account_id=body.to_account_id,
            date=body.date or datetime.utcnow(),
        )
        db.add(t)
        await db.flush()
        await db.refresh(t)
        return {"id": t.id, "category_id": category_id}
