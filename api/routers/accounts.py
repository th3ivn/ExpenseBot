from fastapi import APIRouter

from api.dependencies import CurrentUser, DbSession
from api.schemas.account import AccountCreate, AccountRead, AccountUpdate
from api.services.account import (
    create_account,
    delete_account,
    get_accounts,
    update_account,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountRead])
async def read_all(db: DbSession, user: CurrentUser) -> list[AccountRead]:
    return await get_accounts(db, user.id)


@router.post("", response_model=AccountRead, status_code=201)
async def create(db: DbSession, user: CurrentUser, body: AccountCreate) -> AccountRead:
    return await create_account(db, user.id, body)


@router.put("/{account_id}", response_model=AccountRead)
async def update(
    db: DbSession, user: CurrentUser, account_id: int, body: AccountUpdate
) -> AccountRead:
    return await update_account(db, user.id, account_id, body)


@router.delete("/{account_id}", status_code=204)
async def delete(db: DbSession, user: CurrentUser, account_id: int) -> None:
    await delete_account(db, user.id, account_id)
