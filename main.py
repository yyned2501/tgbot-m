import asyncio
from pyrogram import idle

from app import app, scheduler, logger
from app import models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models

logger.info("主程序启动")


async def main():
    scheduler.start()
    logger.info("app.start()")
    await app.start()
    logger.info("models.create_all()")
    await models.create_all()
    await create_models()
    await idle()
    await app.stop()


if __name__ == "__main__":
    logger.info("主程序main启动")
    asyncio.run(main())
