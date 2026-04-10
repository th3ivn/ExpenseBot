from fastapi import APIRouter
from sqlalchemy import select

from api.dependencies import CurrentUser, DbSession
from api.models.user_settings import UserSettings
from api.schemas.settings import SettingsRead, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


async def _get_or_create_settings(db: DbSession, user_id: int) -> UserSettings:
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)
    return settings


@router.get("", response_model=SettingsRead)
async def read_settings(db: DbSession, user: CurrentUser) -> SettingsRead:
    s = await _get_or_create_settings(db, user.id)
    return SettingsRead.model_validate(s)


@router.put("", response_model=SettingsRead)
async def update_settings(db: DbSession, user: CurrentUser, body: SettingsUpdate) -> SettingsRead:
    s = await _get_or_create_settings(db, user.id)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(s, field, value)
    await db.flush()
    await db.refresh(s)
    return SettingsRead.model_validate(s)
