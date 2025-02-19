import asyncio
from pyrogram import idle
import uvloop

from app import app, scheduler, logger
from app import models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models


async def main():
    logger.info("启动主程序")
    uvloop.install()
    await app.start()
    await models.create_all()
    await create_models()
    scheduler.start()
    logger.info("监听主程序")
    await idle()
    await app.stop()
    logger.info("关闭主程序")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
