import asyncio
import os

import redis
from pyrogram import Client as _Client
from pyrogram import idle

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import models
from app.libs.logs import logger
from app.libs.async_token_bucket import AsyncTokenBucket
from app.config import setting, plugins


class Client(_Client):
    def __init__(self, *arg, **karg):
        super().__init__(*arg, **karg)
        self.bucket = AsyncTokenBucket(capacity=10, fill_rate=1)

    async def invoke(self, *arg, **kargs):
        await self.bucket.consume()
        try:
            return await super().invoke(*arg, **kargs)
        except TimeoutError:
            asyncio.sleep(1)
            return await self.invoke(*arg, **kargs)


os.environ["TZ"] = "Asia/Shanghai"
scheduler = AsyncIOScheduler()

app: Client = None

if setting["proxy"]["enable"]:
    logger.info("proxy start")
    proxy = {
        "scheme": "http",
        "hostname": setting["proxy"]["ip"],
        "port": setting["proxy"]["port"],
        "username": setting["proxy"]["username"],
        "password": setting["proxy"]["password"],
    }
else:
    proxy = None


redis_cli = redis.Redis(
    host=setting["redis"]["host"],
    port=setting["redis"]["port"],
    db=setting["redis"]["db"],
)


async def start_app():
    from app.scripts.zhuque.ex.bet_modes import create_models

    global app
    app = Client(
        "sessions/tgbot",
        api_id=setting["tg"]["api_id"],
        api_hash=setting["tg"]["api_hash"],
        proxy=proxy,
        plugins=dict(root="app.scripts", include=plugins),
    )

    logger.info("启动主程序")
    await app.start()
    await models.create_all()
    await create_models()
    scheduler.start()
    logger.info("监听主程序")
    await idle()
    await app.stop()
    logger.info("关闭主程序")
