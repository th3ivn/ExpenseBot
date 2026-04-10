from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.merchant_rule import MerchantRule


async def auto_categorize(
    db: AsyncSession, user_id: int, merchant: str
) -> int | None:
    """
    Match merchant string against user's merchant_rules.
    Returns category_id of first matching rule (case-insensitive substring match), or None.
    """
    result = await db.execute(
        select(MerchantRule).where(MerchantRule.user_id == user_id)
    )
    rules = result.scalars().all()

    merchant_lower = merchant.lower()
    for rule in rules:
        if rule.merchant_pattern.lower() in merchant_lower:
            return rule.category_id

    return None
