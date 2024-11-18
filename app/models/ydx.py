import logging
import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base
from app.libs.zhuque_requests import get_info
from app.config import setting


logger = logging.getLogger("main")


def test_round(my_bonus, n):
    max_bonus = min(setting["zhuque"]["ydx_model"]["max_bet_bonus"], my_bonus)
    min_bonus = 500
    m = int(min(my_bonus, 1e8) / (2 ** (n + 1)))
    for i in range(m):
        startbonus = m - i
        if startbonus < min_bonus:
            break
        rele_bonus = 0
        sum_bonus = 0
        for i in range(n + 2):
            bonus = sum_bonus / 0.99 + startbonus * (i + 1)
            last_bonus = rele_bonus
            rele_bonus = bonus // min_bonus * min_bonus
            last_sum_bonus = sum_bonus
            sum_bonus += rele_bonus
            if sum_bonus > my_bonus or rele_bonus > max_bonus:
                if i > n:
                    print(i, startbonus, last_bonus, last_sum_bonus)
                    return startbonus
                break


class ZqYdx(Base):
    __tablename__ = "zqydx"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    start_bonus: Mapped[int] = mapped_column(Integer)
    high_times: Mapped[int] = mapped_column(Integer)
    low_times: Mapped[int] = mapped_column(Integer)
    dx: Mapped[int] = mapped_column(Integer, nullable=True)
    bet_switch: Mapped[int] = mapped_column(Integer)
    bet_mode: Mapped[str] = mapped_column(String(8))
    kp_switch: Mapped[int] = mapped_column(Integer)
    betbonus: Mapped[int] = mapped_column(Integer)
    lose_times: Mapped[int] = mapped_column(Integer)
    win_times: Mapped[int] = mapped_column(Integer)
    sum_losebonus: Mapped[int] = mapped_column(Integer)
    message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    bet_round: Mapped[int] = mapped_column(Integer, nullable=True)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime)

    @classmethod
    def init(cls, session: AsyncSession):
        self = cls(
            start_bonus=500,
            high_times=0,
            low_times=0,
            dx=1,
            bet_switch=0,
            bet_mode="A",
            kp_switch=0,
            betbonus=0,
            lose_times=0,
            win_times=0,
            sum_losebonus=0,
            bet_round=0,
            update_time=func.now(),
        )
        session.add(self)
        return self

    async def set_start_bonus(self):
        info = await get_info()
        if info:
            bonus = info["data"]["bonus"]
            start_bonus = test_round(bonus, self.bet_round)
            if start_bonus:
                start_bonus = max(start_bonus, 500)
                self.start_bonus = start_bonus


class YdxHistory(Base):
    __tablename__ = "zqydx_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dx: Mapped[int] = mapped_column(Integer)
