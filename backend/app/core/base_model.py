from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import TIMESTAMP, func


class Base(DeclarativeBase):
    pass


class TimeMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")