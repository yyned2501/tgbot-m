import importlib

from app.config import launch

if launch.get(__name__.split(".")) is not None:
    for sites in launch.get(__name__.split(".")[-1]):
        importlib.import_module(f"{__name__}.{sites}")
