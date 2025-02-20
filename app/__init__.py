import os

import redis
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.libs.logs import logger
from app.libs.async_token_bucket import AsyncTokenBucket
from app.config import setting


class MyClient(Client):
    def __init__(self, *arg, **karg):
        super().__init__(*arg, **karg)
        self.bucket = AsyncTokenBucket(capacity=10, fill_rate=1)

    async def invoke(self, *arg, **kargs):
        await self.bucket.consume()
        return await super().invoke(*arg, **kargs)


os.environ["TZ"] = "Asia/Shanghai"
scheduler = AsyncIOScheduler()

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


app = MyClient(
    "sessions/tgbot",
    api_id=setting["tg"]["api_id"],
    api_hash=setting["tg"]["api_hash"],
    proxy=proxy,
)
redis_cli = redis.Redis(
    host=setting["redis"]["host"],
    port=setting["redis"]["port"],
    db=setting["redis"]["db"],
)
