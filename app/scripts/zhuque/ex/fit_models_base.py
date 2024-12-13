from abc import ABC, abstractmethod

import numpy as np
import openvino as ov

from app import logger
from app.models.ydx import YdxHistory, ZqYdxBase, ZqYdxMulti


core = ov.Core()


class FitModel(ABC):

    def __init__(self, model: ZqYdxMulti):
        self.model = model

    @abstractmethod
    def logger(self):
        pass


class D(FitModel):
    def logger(self):
        f"[倍投]\n当前连败次数:{self.model.losing_streak}|本次下注金额:{self.model.bet_bonus}|累计盈利:{self.model.win_bonus}"
