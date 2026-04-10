from fastapi import APIRouter
from sqlalchemy import select

from api.dependencies import CurrentUser, DbSession
from api.models.tag import Tag
from api.schemas.tag import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
async def read_all(db: DbSession, user: CurrentUser) -> list[TagRead]:
    result = await db.execute(
        select(Tag).where(Tag.user_id == user.id).order_by(Tag.name)
    )
    return [TagRead.model_validate(t) for t in result.scalars().all()]


@router.post("", response_model=TagRead, status_code=201)
async def create(db: DbSession, user: CurrentUser, body: TagCreate) -> TagRead:
    tag = Tag(user_id=user.id, **body.model_dump())
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return TagRead.model_validate(tag)


@router.put("/{tag_id}", response_model=TagRead)
async def update(db: DbSession, user: CurrentUser, tag_id: int, body: TagUpdate) -> TagRead:
    result = await db.execute(select(Tag).where(Tag.id == tag_id, Tag.user_id == user.id))
    tag = result.scalar_one_or_none()
    if tag is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Тег не знайдено")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(tag, field, value)
    await db.flush()
    await db.refresh(tag)
    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
async def delete(db: DbSession, user: CurrentUser, tag_id: int) -> None:
    result = await db.execute(select(Tag).where(Tag.id == tag_id, Tag.user_id == user.id))
    tag = result.scalar_one_or_none()
    if tag is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Тег не знайдено")
    await db.delete(tag)
