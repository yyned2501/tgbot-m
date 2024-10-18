import logging
import random
import datetime

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
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


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
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site: Mapped[str] = mapped_column(String(32))
    today_bonus: Mapped[float] = mapped_column(Float)
    total_bonus: Mapped[float] = mapped_column(Float)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime)

    @classmethod
    async def add(cls, site: str, bonus: float, session: AsyncSession):
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


# class User(Base):
#     __tablename__ = "user"
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#     name: Mapped[str] = mapped_column(String(30))
#     transform: Mapped[list["Transform"]] = relationship(
#         back_populates="user", cascade="all, delete-orphan"
#     )

#     async def get_bonus_sum_for_site(
#         self, session: AsyncSession, site_name: str
#     ) -> int:
#         """
#         获取当前用户在指定站点的bonus总和。

#         :param session: SQLAlchemy session对象
#         :param site_name: 站点名称
#         :return: bonus的总和
#         """
#         bonus_sum_select = select(
#             func.sum(Transform.bonus).filter(
#                 Transform.user_id == self.id, Transform.site == site_name
#             )
#         )
#         bonus_sum = (await session.execute(bonus_sum_select)).scalar_one_or_none()
#         return bonus_sum if bonus_sum is not None else 0


# class Transform(Base):
#     __tablename__ = "transform"
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
#     site: Mapped[str] = mapped_column(String(32))
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     bonus: Mapped[int] = mapped_column(Integer)
#     user: Mapped["User"] = relationship("User", back_populates="transforms")
