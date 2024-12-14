import os

from sqlalchemy import select
from app.models.ydx import ZqYdxMulti

from app import logger
from app.models import ASSession
from app.scripts.zhuque.ex.bet_models_base import A, S, BetModel


model_classes: dict[str, type[BetModel]] = {"A": A, "S": S}
_models: dict[str, BetModel] = {}
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


def create_model_function(func):
    return lambda data: func(data)


root = "app/onnxes"
files = os.listdir("app/onnxes")
files.sort()
for file_name in files:
    model_name = file_name.split("_")[1].upper()
    model_path = f"{root}/{file_name}"
    fit_model_class = model_classes.get(model_name[0])
    if fit_model_class is not None:
        fit_model = fit_model_class(model_path)
        _models[model_name] = fit_model
        _function_registry[model_name] = create_model_function(fit_model.bet_model)


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


async def refresh_model_withdrawal():
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
