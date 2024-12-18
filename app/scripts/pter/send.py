import logging

logger = logging.getLogger("main")
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app


TARGET = -1001833464786


async def send():
    pass


FLAG = False


@app.on_message(filters.chat(TARGET) & filters.regex("有坑了"))
async def youkeng(client: Client, message: Message):
    global FLAG
    if FLAG:
        await send()


@app.on_message(filters.command("pter_send") & filters.reply)
async def get_message(client: Client, message: Message):
    global FLAG
    if message.command[1] == "on":
        FLAG = True
    else:
        FLAG = False
