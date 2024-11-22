import os
from app.models.ydx import ZqYdx, YdxHistory
import openvino as ov
import numpy as np

from app import logger

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
    logger.info(f"选择模式{ov_index}")
    db.dx = model_dx[ov_index]


def mode(func_name, *args, **kwargs):
    func = _function_registry.get(func_name)
    if callable(func):
        return func(*args, **kwargs)
    else:
        logger.error(f"不存在模式 {func_name} ,默认使用模式S1")
        return mode("S1", *args, **kwargs)


@register_function("SA")
def SA(db: ZqYdx, data: list[int]):
    return S(db, data, "app/onnxes/zqydx_s4_1732170956_8_1_5044.onnx")


@register_function("SB")
def SB(db: ZqYdx, data: list[int]):
    return S(db, data, "app/onnxes/zqydx_s4_1732186029_7_5_5024.onnx")


@register_function("SC")
def SC(db: ZqYdx, data: list[int]):
    return S(db, data, "app/onnxes/zqydx_s4_1732186930_7_3_5004.onnx")


@register_function("SD")
def SD(db: ZqYdx, data: list[int]):
    return S(db, data, "app/onnxes/zqydx_s4_1732189871_7_3_5014.onnx")


@register_function("SE")
def SE(db: ZqYdx, data: list[int]):
    return S(db, data, "app/onnxes/zqydx_s4_1732173455_7_3_5050.onnx")


n = 1
for root, dirs, files in os.walk("app/onnxes"):
    for file_name in files:
        model = f"{root}/{file_name}"
        _function_registry[f"S{n}"] = lambda db, data: S(db, data, model)
        n += 1


def get_funcs():
    return _function_registry


def test(db: ZqYdx, data: list[int]):
    loss_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
