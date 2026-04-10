from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.tag import Tag
from api.models.transaction import Transaction, TransactionType
from api.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate


async def _load_transaction(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction:
    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.tags))
        .where(Transaction.id == transaction_id, Transaction.user_id == user_id)
    )
    t = result.scalar_one_or_none()
    if t is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Транзакцію не знайдено")
    return t


async def list_transactions(
    db: AsyncSession,
    user_id: int,
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    type_filter: Optional[TransactionType] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[TransactionRead]:
    query = (
        select(Transaction)
        .options(selectinload(Transaction.tags))
        .where(Transaction.user_id == user_id)
    )
    if period_start:
        query = query.where(Transaction.date >= period_start)
    if period_end:
        query = query.where(Transaction.date <= period_end)
    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)
    if account_id is not None:
        query = query.where(Transaction.account_id == account_id)
    if type_filter is not None:
        query = query.where(Transaction.type == type_filter)

    query = query.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return [TransactionRead.model_validate(t) for t in result.scalars().all()]


async def count_transactions(
    db: AsyncSession,
    user_id: int,
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    type_filter: Optional[TransactionType] = None,
) -> int:
    from sqlalchemy import func as sa_func

    query = select(sa_func.count()).select_from(Transaction).where(Transaction.user_id == user_id)
    if period_start:
        query = query.where(Transaction.date >= period_start)
    if period_end:
        query = query.where(Transaction.date <= period_end)
    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)
    if account_id is not None:
        query = query.where(Transaction.account_id == account_id)
    if type_filter is not None:
        query = query.where(Transaction.type == type_filter)
    result = await db.execute(query)
    return result.scalar_one()


async def get_recent(db: AsyncSession, user_id: int, n: int = 20) -> list[TransactionRead]:
    result = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.tags))
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(n)
    )
    return [TransactionRead.model_validate(t) for t in result.scalars().all()]


async def get_transaction(db: AsyncSession, user_id: int, transaction_id: int) -> TransactionRead:
    t = await _load_transaction(db, transaction_id, user_id)
    return TransactionRead.model_validate(t)


async def create_transaction(
    db: AsyncSession, user_id: int, data: TransactionCreate
) -> TransactionRead:
    tag_ids = data.tag_ids
    payload = data.model_dump(exclude={"tag_ids"})
    t = Transaction(user_id=user_id, **payload)

    if tag_ids:
        tags_result = await db.execute(
            select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        )
        t.tags = list(tags_result.scalars().all())

    db.add(t)
    await db.flush()
    await db.refresh(t)
    return await get_transaction(db, user_id, t.id)


async def update_transaction(
    db: AsyncSession, user_id: int, transaction_id: int, data: TransactionUpdate
) -> TransactionRead:
    t = await _load_transaction(db, transaction_id, user_id)

    update_data = data.model_dump(exclude_none=True, exclude={"tag_ids"})
    for field, value in update_data.items():
        setattr(t, field, value)

    if data.tag_ids is not None:
        tags_result = await db.execute(
            select(Tag).where(Tag.id.in_(data.tag_ids), Tag.user_id == user_id)
        )
        t.tags = list(tags_result.scalars().all())

    await db.flush()
    await db.refresh(t)
    return await get_transaction(db, user_id, t.id)


async def delete_transaction(db: AsyncSession, user_id: int, transaction_id: int) -> None:
    t = await _load_transaction(db, transaction_id, user_id)
    await db.delete(t)
