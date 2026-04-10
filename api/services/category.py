from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.category import Category
from api.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


async def get_categories(db: AsyncSession, user_id: int) -> list[CategoryRead]:
    result = await db.execute(
        select(Category)
        .where(Category.user_id == user_id)
        .order_by(Category.sort_order, Category.id)
    )
    return [CategoryRead.model_validate(c) for c in result.scalars().all()]


async def create_category(db: AsyncSession, user_id: int, data: CategoryCreate) -> CategoryRead:
    cat = Category(user_id=user_id, **data.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return CategoryRead.model_validate(cat)


async def update_category(
    db: AsyncSession, user_id: int, category_id: int, data: CategoryUpdate
) -> CategoryRead:
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Категорію не знайдено")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    await db.flush()
    await db.refresh(cat)
    return CategoryRead.model_validate(cat)


async def delete_category(db: AsyncSession, user_id: int, category_id: int) -> None:
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Категорію не знайдено")
    await db.delete(cat)
