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
def A(db: ZqYdx, history: list[YdxHistory]):
    db.dx = 1


@register_function("B")
def A(db: ZqYdx, history: list[YdxHistory]):
    db.dx = 0


@register_function("C")
def C(db: ZqYdx, history: list[YdxHistory]):
    if db.lose_times > 0:
        db.dx = 1 - db.dx


@register_function("D")
def D(db: ZqYdx, history: list[YdxHistory]):
    dx = history[9]
    db.dx = dx.dx


@register_function("E")
def E(db: ZqYdx, history: list[YdxHistory]):
    dx = history[9]
    db.dx = 1 - dx.dx


@register_function("YA")
def YA(db: ZqYdx, history: list[YdxHistory]):
    global ov_index
    model_dx = [1, 0, history[0].dx, history[9].dx, 1 - history[9].dx]
    if db.lose_times % 2 == 0:
        model_onnx = core.read_model(model="app/onnxes/zqydxA.onnx")
        compiled_model_onnx = core.compile_model(model=model_onnx, device_name="AUTO")
        data = [ydx_history.dx for ydx_history in history]
        data.reverse()
        dummy_input = np.array(data, dtype=np.float32)
        res = compiled_model_onnx(dummy_input)
        output_data = res[0]
        ov_index = np.argmax(output_data, axis=0)
        logger.info(f"选择模式{ov_index}")
    db.dx = model_dx[ov_index]


@register_function("YB")
def YA(db: ZqYdx, history: list[YdxHistory]):
    global ov_index
    model_dx = [1, 0, history[0].dx, history[9].dx, 1 - history[9].dx]
    if db.lose_times % 2 == 0:
        model_onnx = core.read_model(model="app/onnxes/zqydxB.onnx")
        compiled_model_onnx = core.compile_model(model=model_onnx, device_name="AUTO")
        data = [ydx_history.dx for ydx_history in history]
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
        func(*args, **kwargs)
    else:
        logger.error(f"不存在模式 {func_name} ,默认使用模式YA")
        mode("YA", *args, **kwargs)
