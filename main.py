from pyrogram import idle

from app import app, scheduler, models, scripts


async def main():
    await app.start()
    scheduler.start()
    await models.create_all()
    await idle()
    await app.stop()


if __name__ == "__main__":
    app.run(main())
