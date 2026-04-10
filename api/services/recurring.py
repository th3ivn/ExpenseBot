from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.recurring import RecurringTransaction
from api.schemas.recurring import RecurringCreate, RecurringRead, RecurringUpdate


async def list_recurring(db: AsyncSession, user_id: int) -> list[RecurringRead]:
    result = await db.execute(
        select(RecurringTransaction)
        .where(RecurringTransaction.user_id == user_id)
        .order_by(RecurringTransaction.next_date)
    )
    return [RecurringRead.model_validate(r) for r in result.scalars().all()]


async def create_recurring(
    db: AsyncSession, user_id: int, data: RecurringCreate
) -> RecurringRead:
    rec = RecurringTransaction(user_id=user_id, **data.model_dump())
    db.add(rec)
    await db.flush()
    await db.refresh(rec)
    return RecurringRead.model_validate(rec)


async def update_recurring(
    db: AsyncSession, user_id: int, recurring_id: int, data: RecurringUpdate
) -> RecurringRead:
    result = await db.execute(
        select(RecurringTransaction).where(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id,
        )
    )
    rec = result.scalar_one_or_none()
    if rec is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Регулярну транзакцію не знайдено")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rec, field, value)
    await db.flush()
    await db.refresh(rec)
    return RecurringRead.model_validate(rec)


async def delete_recurring(db: AsyncSession, user_id: int, recurring_id: int) -> None:
    result = await db.execute(
        select(RecurringTransaction).where(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id,
        )
    )
    rec = result.scalar_one_or_none()
    if rec is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Регулярну транзакцію не знайдено")
    await db.delete(rec)
