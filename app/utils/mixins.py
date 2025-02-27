from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import mapped_column

from app.core.database import Base


class BaseDBModel(Base):
    __abstract__ = True

    id = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    created_at = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
