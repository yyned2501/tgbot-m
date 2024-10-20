import os

import redis
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.libs.logs import logger
from app.config import setting

os.environ["TZ"] = "Asia/Shanghai"
scheduler = AsyncIOScheduler()
scheduler.start()

if setting["proxy"]["enable"]:
    logger.info("proxy start")
    proxy = {
        "scheme": "http",
        "hostname": setting["proxy"]["ip"],
        "port": setting["proxy"]["port"],
    }
else:
    proxy = None

app = Client(
    "tgbot",
    api_id=setting["tg"]["api_id"],
    api_hash=setting["tg"]["api_hash"],
    proxy=proxy,
)
redis_cli = redis.Redis(
    host=setting["redis"]["host"],
    port=setting["redis"]["port"],
    db=setting["redis"]["db"],
)
