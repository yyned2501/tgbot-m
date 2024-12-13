from abc import ABC, abstractmethod
from typing import overload


import numpy as np
import openvino as ov

from app import logger
from app.models.ydx import ZqYdx


core = ov.Core()


class FitModel(ABC):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = self._load_and_compile_model(model_path)

    def _load_and_compile_model(self, model_path: str) -> ov.CompiledModel:
        model_onnx = core.read_model(model=model_path)
        return core.compile_model(model=model_onnx, device_name="AUTO")

    @abstractmethod
    def bet_model(self, data):
        pass

    def _choose_model(self, data: list[int], model_dx: list[int]) -> int:
        logger.debug(data)
        predicted_index = self._predict(data)
        return model_dx[predicted_index]

    def _predict(self, data: list[int]) -> int:
        dummy_input = np.array(data, dtype=np.float32)
        result = self.model(dummy_input)
        output_data = result[0]
        ov_index = np.argmax(output_data, axis=0)
        logger.debug(f"使用模型{self.model_path}预测，选择模式{ov_index}")
        return ov_index
    
    def max_withdrawal(data: list[int]) -> int:
        s = 0  # 当前累计和
        max_sum = 0  # 累计和的最大值
        min_sum_after_max = float("inf")  # 在最大累计和之后的最小累计和
        max_withdraw = 0  # 最大撤回值

        for dx in data:
            s += dx

            # 更新最大累计和
            if s > max_sum:
                max_sum = s
                min_sum_after_max = s

            # 在达到最大累计和之后，更新最小累计和
            if s < min_sum_after_max:
                min_sum_after_max = s
                withdraw = max_sum - min_sum_after_max
                if withdraw > max_withdraw:
                    max_withdraw = withdraw
        
        return max_withdraw
    def test(self, data: list[int]):
        loss_count = [0 for _ in range(50)]
        turn_loss_count = 0
        win_count = 0
        total_count = 0
        for i in range(40, len(data) + 1):
            data_i = data[i - 40 : i]
            dx = self.bet_model(data_i)
            if i < len(data):
                total_count += 1
                if data[i] == dx:
                    loss_count[turn_loss_count] += 1
                    win_count += 1
                    turn_loss_count = 0
                else:
                    turn_loss_count += 1
        max_nonzero_index = next(
            (
                index
                for index, value in reversed(list(enumerate(loss_count)))
                if value != 0
            ),
            -1,
        )
        return {
            "loss_count": loss_count[: max_nonzero_index + 1],
            "max_nonzero_index": max_nonzero_index,
            "win_rate": win_count / total_count,
            "win_count": 2 * win_count - total_count,
            "turn_loss_count": turn_loss_count,
            "guess": dx,
        }


class A(FitModel):
    def bet_model(self, data):
        a5 = min(int(sum(data[-5:]) / 5 * 2), 1)
        a15 = min(int(sum(data[-15:]) / 15 * 2), 1)
        model_dx = [a5, 1 - a5, a15, 1 - a15]
        return super()._choose_model(data, model_dx)


class S(FitModel):
    def bet_model(self, data):
        model_dx = [1, 0, data[-1], data[-10], 1 - data[-10]]
        return super()._choose_model(data, model_dx)
