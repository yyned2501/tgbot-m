import asyncio
import json
import re
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.filters import custom_filters


TARGET = -1001833464786

n = 1


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"已结算: 结果为 \d (.)")
)
async def get_redpocket_gen(client: Client, message: Message):
    match = message.matches[0]
    dx = match.group(1)
    if dx == "大":
        n = 1
    else:
        n *= 2

    await client.send_message(TARGET, "/ydx")


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"创建时间")
)
async def get_redpocket_gen(client: Client, message: Message):
    for _ in range(n):
        await message.click(1,4)
        await asyncio.sleep(1)