from fastapi import APIRouter

from api.dependencies import CurrentUser, DbSession
from api.schemas.budget import BudgetCreate, BudgetProgress, BudgetRead
from api.services.budget import get_current_budget, upsert_budget

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/current", response_model=BudgetProgress)
async def read_current(db: DbSession, user: CurrentUser) -> BudgetProgress:
    return await get_current_budget(db, user.id)


@router.post("", response_model=BudgetRead, status_code=201)
async def create_or_update(db: DbSession, user: CurrentUser, body: BudgetCreate) -> BudgetRead:
    return await upsert_budget(db, user.id, body)
