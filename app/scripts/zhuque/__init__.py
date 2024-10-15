import importlib

from app.config import launch

method = __name__.split(".")[-2]
site = __name__.split(".")[-1]
for task in launch.get(method).get(site):
    importlib.import_module(f"{__name__}.{task}")
