import os

from sqlalchemy import select
from app.models.ydx import ZqYdx, ZqYdxMulti
import openvino as ov
import numpy as np

from app import logger
from app.models import ASSession

core = ov.Core()


_function_registry = {}
_compiled_model_onnx = {}


def register_function(name):
    def decorator(func):
        _function_registry[name] = func
        return func

    return decorator


def S(data: list[int], onnx_file):
    model_dx = [1, 0, data[-1], data[-10], 1 - data[-10]]
    compiled_model_onnx = _compiled_model_onnx[onnx_file]
    logger.debug(data)
    dummy_input = np.array(data, dtype=np.float32)
    res = compiled_model_onnx(dummy_input)
    output_data = res[0]
    ov_index = np.argmax(output_data, axis=0)
    logger.debug(f"使用模型{onnx_file}预测，选择模式{ov_index}")
    return model_dx[ov_index]


def A(data: list[int], onnx_file):
    a5 = max(int(sum(data[-5:]) / 5 * 2),1)
    a15 = max(int(sum(data[-15:]) / 5 * 2),1)
    model_dx = [a5, 1 - a5, a15, 1 - a15]
    compiled_model_onnx = _compiled_model_onnx[onnx_file]
    logger.debug(data)
    dummy_input = np.array(data, dtype=np.float32)
    res = compiled_model_onnx(dummy_input)
    output_data = res[0]
    ov_index = np.argmax(output_data, axis=0)
    logger.debug(f"使用模型{onnx_file}预测，选择模式{ov_index}")
    return model_dx[ov_index]


def mode(func_name, *args, **kwargs):
    func = _function_registry.get(func_name)
    if callable(func):
        return func(*args, **kwargs)
    else:
        logger.error(f"不存在模式 {func_name} ,默认使用模式S1")
        return mode("S1", *args, **kwargs)


def create_model_function(model, model_name):
    model_onnx = core.read_model(model=model)
    compiled_model_onnx = core.compile_model(model=model_onnx, device_name="AUTO")
    _compiled_model_onnx[model] = compiled_model_onnx
    if model_name[0] == "S":
        return lambda data: S(data, model)
    elif model_name[0] == "A":
        return lambda data: A(data, model)


root = "app/onnxes"
files = os.listdir("app/onnxes")
files.sort()
for file_name in files:
    model_name = file_name.split("_")[1].upper()
    model = f"{root}/{file_name}"
    _function_registry[model_name] = create_model_function(model, model_name)


def get_funcs():
    return _function_registry


def test(db: ZqYdx, data: list[int]):
    data.reverse()
    n = 1
    ret = {}
    for model in _function_registry:
        loss_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        turn_loss_count = 0
        win_count = 0
        total_count = 0
        for i in range(40, len(data) + 1):
            data_i = data[i - 40 : i]
            dx = mode(model, data_i)
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
        ret[model] = {
            "loss_count": loss_count[: max_nonzero_index + 1],
            "max_nonzero_index": max_nonzero_index,
            "win_rate": win_count / total_count,
            "win_count": 2 * win_count - total_count,
            "turn_loss_count": turn_loss_count,
            "guess": dx,
        }
        n += 1
    return ret


async def create_models():
    session = ASSession()
    models_dict = {}
    async with session.begin():
        models = await session.execute(select(ZqYdxMulti))
        for model in models.scalars():
            if model.name not in _function_registry:
                await session.delete(model)
            else:
                models_dict[model.name] = model
        for model_name in _function_registry:
            if model_name not in models_dict:
                session.add(ZqYdxMulti(name=model_name))
