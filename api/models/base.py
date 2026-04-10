from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
    pass


def now_utc() -> datetime:
    return datetime.utcnow()


def updated_at_col() -> MappedColumn:
    return mapped_column(
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )
