import logging
from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    Float,
    BigInteger,
    Text,
    TIMESTAMP,
    SmallInteger,
    DateTime,
    Enum,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import random
import datetime

from app.models.base import Base


logger = logging.getLogger("main")


class Redpocket(Base):
    __tablename__ = "redpockets"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site: Mapped[str] = mapped_column(String(32))
    bonus: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
