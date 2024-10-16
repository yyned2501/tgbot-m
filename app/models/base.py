from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    create_time: Mapped[int] = mapped_column(DateTime, default=func.now())
