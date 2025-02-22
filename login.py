import asyncio
import subprocess

from pyrogram import Client

from app.libs.logs import logger
from app.config import setting


if setting["proxy"]["enable"]:
    logger.info("proxy start")
    proxy = {
        "scheme": "http",
        "hostname": setting["proxy"]["ip"],
        "port": setting["proxy"]["port"],
    }
else:
    proxy = None


async def main():
    app = Client(
        "sessions/tgbot",
        api_id=setting["tg"]["api_id"],
        api_hash=setting["tg"]["api_hash"],
        proxy=proxy,
    )
    async with app:
        await app.send_message("me", "登录成功")
    print("登录成功")
    command = ["supervisorctl", "start", "main"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("启动main成功")
    else:
        print(result.stdout)
        print(result.stderr)


if __name__ == "__main__":
    asyncio.run(main())
