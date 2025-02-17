import logging

from sqlalchemy import (
    String,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models import ASSession
from app.models.base import Base, CreateTimeBase
from app.libs.zhuque_requests import get_info


logger = logging.getLogger("main")


class YdxHistory(CreateTimeBase):
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
        if self.bet_round:
            max_bonus = min(self.max_bet_bonus, self.user_bonus, 5e7)
            min_bonus = 500
            self.start_bonus = (
                max_bonus / (2**self.bet_round - 1) // min_bonus * min_bonus
            )


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
