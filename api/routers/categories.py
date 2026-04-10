from fastapi import APIRouter

from api.dependencies import CurrentUser, DbSession
from api.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from api.services.category import (
    create_category,
    delete_category,
    get_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def read_all(db: DbSession, user: CurrentUser) -> list[CategoryRead]:
    return await get_categories(db, user.id)


@router.post("", response_model=CategoryRead, status_code=201)
async def create(db: DbSession, user: CurrentUser, body: CategoryCreate) -> CategoryRead:
    return await create_category(db, user.id, body)


@router.put("/{category_id}", response_model=CategoryRead)
async def update(
    db: DbSession, user: CurrentUser, category_id: int, body: CategoryUpdate
) -> CategoryRead:
    return await update_category(db, user.id, category_id, body)


@router.delete("/{category_id}", status_code=204)
async def delete(db: DbSession, user: CurrentUser, category_id: int) -> None:
    await delete_category(db, user.id, category_id)
