from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.account import Account
from api.models.transaction import Transaction, TransactionType
from api.schemas.account import AccountCreate, AccountRead, AccountUpdate


async def get_accounts(db: AsyncSession, user_id: int) -> list[AccountRead]:
    result = await db.execute(
        select(Account)
        .where(Account.user_id == user_id)
        .order_by(Account.sort_order, Account.id)
    )
    accounts = result.scalars().all()

    out: list[AccountRead] = []
    for acc in accounts:
        balance = await compute_balance(db, acc)
        read = AccountRead.model_validate(acc)
        read.current_balance = balance
        out.append(read)
    return out


async def compute_balance(db: AsyncSession, account: Account) -> Decimal:
    income_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.account_id == account.id,
            Transaction.type == TransactionType.income,
        )
    )
    income: Decimal = income_result.scalar_one()

    expense_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.account_id == account.id,
            Transaction.type == TransactionType.expense,
        )
    )
    expense: Decimal = expense_result.scalar_one()

    transfers_out_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.account_id == account.id,
            Transaction.type == TransactionType.transfer,
        )
    )
    transfers_out: Decimal = transfers_out_result.scalar_one()

    transfers_in_result = await db.execute(
        select(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
        .where(
            Transaction.to_account_id == account.id,
            Transaction.type == TransactionType.transfer,
        )
    )
    transfers_in: Decimal = transfers_in_result.scalar_one()

    return account.opening_balance + income - expense + transfers_in - transfers_out


async def create_account(db: AsyncSession, user_id: int, data: AccountCreate) -> AccountRead:
    acc = Account(user_id=user_id, **data.model_dump())
    db.add(acc)
    await db.flush()
    await db.refresh(acc)
    balance = await compute_balance(db, acc)
    read = AccountRead.model_validate(acc)
    read.current_balance = balance
    return read


async def update_account(
    db: AsyncSession, user_id: int, account_id: int, data: AccountUpdate
) -> AccountRead:
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )
    acc = result.scalar_one_or_none()
    if acc is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Рахунок не знайдено")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(acc, field, value)
    await db.flush()
    await db.refresh(acc)
    balance = await compute_balance(db, acc)
    read = AccountRead.model_validate(acc)
    read.current_balance = balance
    return read


async def delete_account(db: AsyncSession, user_id: int, account_id: int) -> None:
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )
    acc = result.scalar_one_or_none()
    if acc is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Рахунок не знайдено")
    await db.delete(acc)
