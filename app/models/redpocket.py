import logging
import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    func,
)
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column


from app.models.base import Base
from app.models import ASSession

logger = logging.getLogger("main")


def is_today(last_date: datetime.datetime):
    try:
        current_date = datetime.datetime.now()
        return last_date.date() == current_date.date()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False


class Redpocket(Base):
    __tablename__ = "redpockets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site: Mapped[str] = mapped_column(String(32))
    today_bonus: Mapped[float] = mapped_column(Float)
    total_bonus: Mapped[float] = mapped_column(Float)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime)

    @classmethod
    async def add(cls, site: str, bonus: float):
        session = ASSession()
        self = (
            await session.execute(select(Redpocket).filter(Redpocket.site == site))
        ).scalar_one_or_none()
        if not self:
            self = cls(site=site, today_bonus=0, total_bonus=0, update_time=func.now())
            session.add(self)
        await self.add_(bonus)
        return self

    async def add_(self, bonus: float):
        if not is_today(self.update_time):
            self.today_bonus = 0
        self.today_bonus += bonus
        self.total_bonus += bonus
        self.update_time = func.now()
