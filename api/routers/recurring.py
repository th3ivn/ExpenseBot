from fastapi import APIRouter

from api.dependencies import CurrentUser, DbSession
from api.schemas.recurring import RecurringCreate, RecurringRead, RecurringUpdate
from api.services.recurring import (
    create_recurring,
    delete_recurring,
    list_recurring,
    update_recurring,
)

router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.get("", response_model=list[RecurringRead])
async def read_all(db: DbSession, user: CurrentUser) -> list[RecurringRead]:
    return await list_recurring(db, user.id)


@router.post("", response_model=RecurringRead, status_code=201)
async def create(db: DbSession, user: CurrentUser, body: RecurringCreate) -> RecurringRead:
    return await create_recurring(db, user.id, body)


@router.put("/{recurring_id}", response_model=RecurringRead)
async def update(
    db: DbSession, user: CurrentUser, recurring_id: int, body: RecurringUpdate
) -> RecurringRead:
    return await update_recurring(db, user.id, recurring_id, body)


@router.delete("/{recurring_id}", status_code=204)
async def delete(db: DbSession, user: CurrentUser, recurring_id: int) -> None:
    await delete_recurring(db, user.id, recurring_id)
