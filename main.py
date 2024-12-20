from pyrogram import idle

from app import app, scheduler, models, scripts, schedulers
from app.scripts.zhuque.ex.bet_modes import create_models


async def main():
    await app.start()
    scheduler.start()
    await models.create_all()
    await create_models()
    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
