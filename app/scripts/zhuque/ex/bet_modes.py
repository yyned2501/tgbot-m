import os

from sqlalchemy import select
from app.models.ydx import ZqYdx, ZqYdxMulti
import openvino as ov
import numpy as np

from app import logger
from app.models import ASSession

core = ov.Core()

ov_index = 0


_function_registry = {}


def register_function(name):
    def decorator(func):
        _function_registry[name] = func
        return func

    return decorator


@register_function("A")
def A(db: ZqYdx, data: list[int]):
    db.dx = 1


@register_function("B")
def A(db: ZqYdx, data: list[int]):
    db.dx = 0


@register_function("C")
def C(db: ZqYdx, data: list[int]):
    if db.lose_times > 0:
        db.dx = 1 - db.dx


@register_function("D")
def D(db: ZqYdx, data: list[int]):
    db.dx = data[9]


@register_function("E")
def E(db: ZqYdx, data: list[int]):
    db.dx = 1 - data[9]


def S(db: ZqYdx, data: list[int], onnx_file):
    model_dx = [1, 0, data[0], data[9], 1 - data[9]]
    model_onnx = core.read_model(model=onnx_file)
    compiled_model_onnx = core.compile_model(model=model_onnx, device_name="AUTO")
    data.reverse()
    dummy_input = np.array(data, dtype=np.float32)
    res = compiled_model_onnx(dummy_input)
    output_data = res[0]
    ov_index = np.argmax(output_data, axis=0)
    logger.info(f"使用模型{onnx_file}预测，选择模式{ov_index}")
    db.dx = model_dx[ov_index]


def mode(func_name, *args, **kwargs):
    func = _function_registry.get(func_name)
    if callable(func):
        return func(*args, **kwargs)
    else:
        logger.error(f"不存在模式 {func_name} ,默认使用模式S1")
        return mode("S1", *args, **kwargs)


def create_model_function(model):
    return lambda db, data: S(db, data, model)


n = 1
for root, dirs, files in os.walk("app/onnxes"):
    for file_name in files:
        model = f"{root}/{file_name}"
        _function_registry[f"S{n}"] = create_model_function(model)
        n += 1


def get_funcs():
    return _function_registry


def test(db: ZqYdx, data: list[int]):
    data.reverse()
    n = 1
    ret = {}
    for root, dirs, files in os.walk("app/onnxes"):
        for file_name in files:
            loss_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            turn_loss_count = 0
            win_count = 0
            total_count = 0
            mode = 0
            if file_name.startswith("zqydx_s4"):
                model = f"{root}/{file_name}"
                model_name = f"S{n}"
                model_onnx = core.read_model(model=model)
                compiled_model_onnx = core.compile_model(
                    model=model_onnx, device_name="AUTO"
                )
                for i in range(40, len(data) + 1):
                    model_dx = [1, 0, data[i - 1], data[i - 10], 1 - data[i - 10]]
                    d = data[i - 40 : i]
                    d = np.array(d, dtype=np.float32)
                    res = compiled_model_onnx(d)
                    mode = np.argmax(res[0], axis=0)
                    if i < len(data):
                        total_count += 1
                        if data[i] == model_dx[mode]:
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
                ret[model_name] = {
                    "file": file_name,
                    "loss_count": loss_count[: max_nonzero_index + 1],
                    "max_nonzero_index": max_nonzero_index,
                    "win_rate": win_count / total_count,
                    "win_count": 2 * win_count - total_count,
                    "turn_loss_count": turn_loss_count,
                    "guess": model_dx[mode],
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
