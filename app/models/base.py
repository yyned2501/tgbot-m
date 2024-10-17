import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
