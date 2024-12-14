import importlib

from app.config import launch

for sites in launch.get(__name__.split(".")[-1]):
    importlib.import_module(f"{__name__}.{sites}")
