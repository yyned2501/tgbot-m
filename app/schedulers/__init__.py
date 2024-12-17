import importlib

from app.config import launch
from app import logger
logger.info("加载定时任务")
logger.info(__name__.split(".")[-1])
if launch.get(__name__.split(".")[-1]):
    for sites in launch.get(__name__.split(".")[-1]):
        logger.info(f"{__name__}.{sites}")
        importlib.import_module(f"{__name__}.{sites}")
