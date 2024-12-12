import os

from sqlalchemy import select
from app.models.ydx import ZqYdxMulti
import openvino as ov

from app import logger
from app.models import ASSession
from app.scripts.zhuque.ex.fit_models import A, S, FitModel

core = ov.Core()

_models: dict[str, FitModel] = {}
_function_registry = {}


def register_function(name):
    def decorator(func):
        _function_registry[name] = func
        return func

    return decorator


def mode(func_name, *args, **kwargs):
    func = _function_registry.get(func_name)
    if callable(func):
        return func(*args, **kwargs)
    else:
        logger.error(f"不存在模式 {func_name} ,默认使用模式S1")
        return mode("S1", *args, **kwargs)


root = "app/onnxes"
files = os.listdir("app/onnxes")
files.sort()
for file_name in files:
    model_name = file_name.split("_")[1].upper()
    model_path = f"{root}/{file_name}"
    fit_model = None
    if model_name[0] == "S":
        fit_model = S(model_path)
    elif model_name[0] == "A":
        fit_model = A(model_path)
    if fit_model:
        _models[model_name] = fit_model
        _function_registry[model_name] = lambda data: fit_model.bet_model(data)


def get_funcs():
    return _function_registry


def test(data: list[int]):
    data.reverse()
    ret = {}
    for model in _models:
        ret[model] = _models[model].test(data)
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
        for model_name in _models:
            if model_name not in models_dict:
                session.add(ZqYdxMulti(name=model_name))
