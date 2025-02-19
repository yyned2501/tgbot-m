from pyrogram import idle

from app import app, scheduler
from app import models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models


async def main():
    await app.start()
    await models.create_all()
    await create_models()
    scheduler.start()
    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
