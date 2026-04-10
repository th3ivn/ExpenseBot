from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from api.dependencies import CurrentUser, DbSession
from api.models.transaction import TransactionType
from api.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from api.services.transaction import (
    count_transactions,
    create_transaction,
    delete_transaction,
    get_recent,
    get_transaction,
    list_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/count")
async def read_count(
    db: DbSession,
    user: CurrentUser,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    category_id: Optional[int] = Query(None),
    account_id: Optional[int] = Query(None),
    type: Optional[TransactionType] = Query(None),
) -> dict:
    total = await count_transactions(
        db, user.id, period_start, period_end, category_id, account_id, type
    )
    return {"count": total}


@router.get("", response_model=list[TransactionRead])
async def read_transactions(
    db: DbSession,
    user: CurrentUser,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    category_id: Optional[int] = Query(None),
    account_id: Optional[int] = Query(None),
    type: Optional[TransactionType] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[TransactionRead]:
    return await list_transactions(
        db, user.id, period_start, period_end, category_id, account_id, type, limit, offset
    )


@router.get("/recent", response_model=list[TransactionRead])
async def read_recent(
    db: DbSession,
    user: CurrentUser,
    n: int = Query(20, ge=1, le=100),
) -> list[TransactionRead]:
    return await get_recent(db, user.id, n)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def read_one(db: DbSession, user: CurrentUser, transaction_id: int) -> TransactionRead:
    return await get_transaction(db, user.id, transaction_id)


@router.post("", response_model=TransactionRead, status_code=201)
async def create(db: DbSession, user: CurrentUser, body: TransactionCreate) -> TransactionRead:
    return await create_transaction(db, user.id, body)


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update(
    db: DbSession, user: CurrentUser, transaction_id: int, body: TransactionUpdate
) -> TransactionRead:
    return await update_transaction(db, user.id, transaction_id, body)


@router.delete("/{transaction_id}", status_code=204)
async def delete(db: DbSession, user: CurrentUser, transaction_id: int) -> None:
    await delete_transaction(db, user.id, transaction_id)
