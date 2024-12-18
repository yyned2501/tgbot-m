import logging
import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models import ASSession
from app.models.base import Base
from app.libs.zhuque_requests import get_info


logger = logging.getLogger("main")


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
    user_bonus: Mapped[int] = mapped_column(Integer)
    max_bet_bonus: Mapped[int] = mapped_column(Integer)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime)

    @classmethod
    def init(cls):
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
            user_bonus=0,
            max_bet_bonus=50000000,
            update_time=func.now(),
        )
        ASSession.add(self)
        return self

    async def set_start_bonus(self):
        if self.bet_round:
            info = await get_info()
            if info:
                self.user_bonus = int(info["data"]["bonus"])
                self.max_bet_bonus = min(int(self.user_bonus / 4 // 500 * 500), 5e7)
            self.test_round()

    def test_round(self):
        max_bonus = min(self.max_bet_bonus, self.user_bonus, 5e7)
        min_bonus = 500
        m = min(
            (
                int(
                    min(self.user_bonus, 1e8)
                    / (2 ** (self.bet_round + 2) - self.bet_round - 2)
                    / 0.99**self.bet_round
                )
                // 500
                + 1
            )
            * 500,
            (
                int(
                    min(max_bonus, 1e8)
                    / (2 ** (self.bet_round + 1) - 1)
                    / 0.99 ** (self.bet_round - 1)
                )
                // 500
                + 1
            )
            * 500,
        )
        for i in range(m):
            startbonus = m - i
            if startbonus < min_bonus:
                break
            bet_bonus = 0
            sum_bonus = 0
            for i in range(self.bet_round + 2):
                bonus = sum_bonus / 0.99 + startbonus * (i + 1)
                last_bonus = bet_bonus
                bet_bonus = bonus // min_bonus * min_bonus
                last_sum_bonus = sum_bonus
                sum_bonus += bet_bonus
                if sum_bonus > self.user_bonus or bet_bonus > max_bonus:
                    if i > self.bet_round:
                        logger.debug(
                            f"{i}, {startbonus}, {last_bonus}, {last_sum_bonus}"
                        )
                        self.start_bonus = startbonus
                        return
                    break


class YdxHistory(Base):
    __tablename__ = "zqydx_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dx: Mapped[int] = mapped_column(Integer)


class ZqYdxBase(Base):
    __tablename__ = "zqydx_base"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kp_switch: Mapped[int] = mapped_column(Integer)
    message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    bet_switch: Mapped[int] = mapped_column(Integer)
    start_bonus: Mapped[int] = mapped_column(Integer)
    bet_round: Mapped[int] = mapped_column(Integer, nullable=True)
    user_bonus: Mapped[int] = mapped_column(Integer)
    max_bet_bonus: Mapped[int] = mapped_column(Integer)

    @classmethod
    def init(cls):
        self = cls(
            start_bonus=500,
            kp_switch=0,
            bet_switch=0,
            user_bonus=0,
            max_bet_bonus=10000000,
        )
        ASSession.add(self)
        return self

    async def set_start_bonus(self, bonus=None):
        if self.bet_round:
            if not bonus:
                info = await get_info()
                if info:
                    bonus = info["data"]["bonus"]
            if bonus:
                self.user_bonus = int(bonus)
                self.max_bet_bonus = min(int(self.user_bonus / 4 // 500 * 500), 5e7)
            self.test_round()

    def test_round(self):
        max_bonus = min(self.max_bet_bonus, self.user_bonus, 5e7)
        min_bonus = 500
        m = min(
            (
                int(
                    min(self.user_bonus, 1e8)
                    / (2 ** (self.bet_round + 2) - self.bet_round - 2)
                    / 0.99**self.bet_round
                )
                // 500
                + 1
            )
            * 500,
            (
                int(
                    min(max_bonus, 1e8)
                    / (2 ** (self.bet_round + 1) - 1)
                    / 0.99 ** (self.bet_round - 1)
                )
                // 500
                + 1
            )
            * 500,
        )
        for i in range(m):
            startbonus = m - i
            if startbonus < min_bonus:
                break
            bet_bonus = 0
            sum_bonus = 0
            for i in range(self.bet_round + 2):
                bonus = sum_bonus / 0.99 + startbonus * (i + 1)
                last_bonus = bet_bonus
                bet_bonus = bonus // min_bonus * min_bonus
                last_sum_bonus = sum_bonus
                sum_bonus += bet_bonus
                if sum_bonus > self.user_bonus or bet_bonus > max_bonus:
                    if i > self.bet_round:
                        logger.debug(
                            f"{i}, {startbonus}, {last_bonus}, {last_sum_bonus}"
                        )
                        self.start_bonus = startbonus
                        return
                    break


class ZqYdxMulti(Base):
    __tablename__ = "zqydx_models"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(8))
    bonus: Mapped[int] = mapped_column(Integer, default=500)
    bet_switch: Mapped[int] = mapped_column(Integer, default=1)
    fit_model: Mapped[str] = mapped_column(String(8), default="D")
    win: Mapped[int] = mapped_column(Integer, default=0)
    lose: Mapped[int] = mapped_column(Integer, default=0)
    winning_streak: Mapped[int] = mapped_column(Integer, default=0)
    losing_streak: Mapped[int] = mapped_column(Integer, default=0)
    max_withdrawal: Mapped[int] = mapped_column(Integer, default=0)
    current_withdrawal: Mapped[int] = mapped_column(Integer, default=0)
    bet_bonus: Mapped[int] = mapped_column(Integer, default=0)
    sum_losebonus: Mapped[int] = mapped_column(Integer, default=0)
    win_bonus: Mapped[int] = mapped_column(Integer, default=0)
