import asyncio
from pyrogram import idle

from app import app, scheduler, logger
from app import models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models


async def main():
    logger.info("启动主程序")
    await app.start()
    await models.create_all()
    await create_models()
    scheduler.start()
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
