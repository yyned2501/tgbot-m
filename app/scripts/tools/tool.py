import asyncio
import logging
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app

logger = logging.getLogger("main")
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


@app.on_message(filters.command("getmessage") & filters.reply)
async def get_message(client: Client, message: Message):
    with open("message.json", "w") as f:
        f.write(str(message.reply_to_message))
    await client.send_document("me", "message.json")


@app.on_message(filters.command("setloglevel"))
async def get_message(client: Client, message: Message):
    level = message.command[1].upper()
    if level in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[level])
        await message.edit(f"已将日志调整为{level}")
    await asyncio.sleep(5)
    await message.delete()
