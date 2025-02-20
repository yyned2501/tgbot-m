import sys

if sys.platform != "win32":
    import uvloop

    uvloop.install()


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
    logger.info("监听主程序")
    await idle()
    await app.stop()
    logger.info("关闭主程序")


if __name__ == "__main__":
    app.run(main())
