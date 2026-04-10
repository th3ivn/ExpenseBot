from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    categories: Mapped[list["Category"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    tags: Mapped[list["Tag"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    budgets: Mapped[list["Budget"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    recurring_transactions: Mapped[list["RecurringTransaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    merchant_rules: Mapped[list["MerchantRule"]] = relationship(back_populates="user", cascade="all, delete-orphan")  # noqa: F821
    settings: Mapped[Optional["UserSettings"]] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)  # noqa: F821
