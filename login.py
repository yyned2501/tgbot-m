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

app = Client(
    "sessions/tgbot",
    api_id=setting["tg"]["api_id"],
    api_hash=setting["tg"]["api_hash"],
    proxy=proxy,
)


async def main():
    command = ["supervisorctl", "restart", "main"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("重启成功")
    else:
        print(result.stdout)
        print(result.stderr)


if __name__ == "__main__":
    app.run(main())
