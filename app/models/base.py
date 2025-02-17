import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class CreateTimeBase(Base):
    __abstract__ = True
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class TimeBase(Base):
    __abstract__ = True
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
    update_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
