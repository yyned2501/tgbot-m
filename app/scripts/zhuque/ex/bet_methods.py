from abc import ABC, abstractmethod

import openvino as ov

from app.models.ydx import ZqYdxModels, ZqYdxMethods, ZqYdxBaseNew, ZqYdxRuns


core = ov.Core()
grids = [0]
grids_need = [0]
for i in range(1, 40):
    last_g = grids[i - 1]
    grids.append(last_g / 0.99 + 1)
    grids_need.append(sum(grids))

double = [1]
double_need = [1]
for i in range(1, 15):
    current_lose_bonus = double_need[i - 1]
    double.append(current_lose_bonus / 0.99 + 1)
    grids_need.append(sum(grids))


class BetMethod(ABC):
    def __init__(
        self,
        method: ZqYdxMethods,
        model: ZqYdxModels,
        base: ZqYdxBaseNew,
        run: ZqYdxRuns,
    ):
        self.base = base
        self.method = method
        self.model = model
        self.run = run

    @abstractmethod
    def bet_bonus(self):
        pass

    @abstractmethod
    def fresh_bonus(self):
        pass


class D(BetMethod):
    def bet_bonus(self):
        return int(
            self.run.current_lose_bonus / 0.99
            + (self.model.losing_streak + 1) * self.method.start_bonus
        )

    def fresh_bonus(self):
        if self.model.losing_streak == 0:
            return int(
                min(
                    self.base.user_bonus / double_need[self.method.max_lose_times],
                    self.base.max_bet_bonus / double[self.method.max_lose_times],
                )
            )
