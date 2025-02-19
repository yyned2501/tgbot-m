import logging
from pyrogram import idle

from app import app, scheduler
from app import models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models

logger = logging.getLogger("main")


async def main():
    await app.start()
    logger.info("app.start()")
    await models.create_all()
    logger.info("models.create_all()")
    await create_models()
    logger.info("create_models()")
    scheduler.start()
    logger.info("scheduler.start()")
    logger.info(scheduler.get_jobs())
    logger.info("logger.info(scheduler.get_jobs())")
    await idle()
    logger.info("idle()")
    await app.stop()


if __name__ == "__main__":
    app.run(main())
