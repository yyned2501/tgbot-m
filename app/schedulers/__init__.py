import importlib

from app.config import launch

if launch.get(__name__.split(".")[-1]):
    for sites in launch.get(__name__.split(".")[-1]):
        importlib.import_module(f"{__name__}.{sites}")
