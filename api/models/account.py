from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    emoji: Mapped[str] = mapped_column(String(16), nullable=False, default="💳")
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="accounts")  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="account",
        foreign_keys="Transaction.account_id",
    )
    transfers_in: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="to_account",
        foreign_keys="Transaction.to_account_id",
    )
    recurring_transactions: Mapped[list["RecurringTransaction"]] = relationship(  # noqa: F821
        back_populates="account",
        foreign_keys="RecurringTransaction.account_id",
    )
