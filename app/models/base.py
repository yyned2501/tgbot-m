import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class CreateTimeBase(Base):
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class TimeBase(Base):
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
