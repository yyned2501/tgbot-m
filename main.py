import logging
from pyrogram import idle

from app import app, scheduler
from app import models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models


async def main():
    await app.start()
    print("app.start()")
    await models.create_all()
    print("models.create_all()")
    await create_models()
    print("create_models()")
    scheduler.start()
    print("scheduler.start()")
    print(scheduler.get_jobs())
    print("logger.info(scheduler.get_jobs())")
    await idle()
    print("idle()")
    await app.stop()


if __name__ == "__main__":
    app.run(main())
