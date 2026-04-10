from fastapi import APIRouter

from api.auth.telegram import verify_init_data
from api.config import settings
from api.dependencies import DbSession
from api.models.user import User
from sqlalchemy import select
from pydantic import BaseModel


router = APIRouter(prefix="/auth", tags=["auth"])


class ValidateRequest(BaseModel):
    init_data: str


class ValidateResponse(BaseModel):
    token: str
    user_id: int
    telegram_id: int
    first_name: str
    username: str | None


@router.post("/validate", response_model=ValidateResponse)
async def validate(body: ValidateRequest, db: DbSession) -> ValidateResponse:
    try:
        tg_user = verify_init_data(body.init_data, settings.BOT_TOKEN)
    except ValueError as exc:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    telegram_id: int = tg_user["id"]
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            first_name=tg_user.get("first_name", ""),
            username=tg_user.get("username"),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    return ValidateResponse(
        token=body.init_data,
        user_id=user.id,
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        username=user.username,
    )
