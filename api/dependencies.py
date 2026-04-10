from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.telegram import verify_init_data
from api.config import settings
from api.database.session import get_db
from api.models.user import User


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Відсутній токен авторизації",
        )

    init_data = authorization.removeprefix("Bearer ")

    try:
        tg_user = verify_init_data(init_data, settings.BOT_TOKEN)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

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

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
