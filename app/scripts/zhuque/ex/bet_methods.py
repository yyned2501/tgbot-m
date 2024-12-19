from abc import ABC, abstractmethod

import numpy as np
import openvino as ov

from app import logger
from app.models.ydx import YdxHistory, ZqYdxBase, ZqYdxMulti


core = ov.Core()
grids = [0]
grids_need = [0]
for i in range(1, 40):
    last_g = grids[i - 1]
    grids.append(last_g / 0.99 + 1)
    grids_need.append(sum(grids))


class FitModel(ABC):

    def __init__(self, model: ZqYdxMulti, base: ZqYdxBase):
        self.model = model
        self.base = base
        self.bonus = 0

    @abstractmethod
    def logger(self):
        pass

    @abstractmethod
    def bet_bonus(self):
        pass

    @abstractmethod
    def fresh_bonus(self):
        pass


class D(FitModel):
    def bet_bonus(self):
        return int(
            self.model.sum_losebonus / 0.99
            + (self.model.losing_streak + 1) * self.bonus
        )

    def fresh_bonus(self):
        pass


class G(FitModel):
    def bet_bonus(self):
        return int(grids[min(self.model.lose - self.model.win, 39)] * self.bonus)
