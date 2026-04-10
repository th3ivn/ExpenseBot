import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Table,
    Column,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class TransactionType(str, enum.Enum):
    expense = "expense"
    income = "income"
    transfer = "transfer"


transaction_tags = Table(
    "transaction_tags",
    Base.metadata,
    Column("transaction_id", Integer, ForeignKey("transactions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    to_account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="transactions")  # noqa: F821
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")  # noqa: F821
    account: Mapped["Account"] = relationship(  # noqa: F821
        back_populates="transactions",
        foreign_keys=[account_id],
    )
    to_account: Mapped[Optional["Account"]] = relationship(  # noqa: F821
        back_populates="transfers_in",
        foreign_keys=[to_account_id],
    )
    tags: Mapped[list["Tag"]] = relationship(secondary=transaction_tags, back_populates="transactions")  # noqa: F821
