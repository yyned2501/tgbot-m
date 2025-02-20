import sys

if sys.platform != "win32":
    import uvloop

    uvloop.install()

import asyncio

from pyrogram import idle
from app import Client, scheduler, logger, setting, proxy
from app import models
from app.scripts.zhuque.ex.bet_modes import create_models


async def main():
    app = Client(
        "sessions/tgbot",
        api_id=setting["tg"]["api_id"],
        api_hash=setting["tg"]["api_hash"],
        proxy=proxy,
        plugins=dict(root="app", exclude=["scripts.zhuque.ydx_multi"]),
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


if __name__ == "__main__":
    asyncio.run(main())
