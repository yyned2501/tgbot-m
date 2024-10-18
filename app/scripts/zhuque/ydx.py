import asyncio
import json
import re
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.filters import custom_filters


TARGET = -1001833464786

n = 1
d = 0
x = 0


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"已结算: 结果为 \d (.)")
)
async def get_redpocket_gen(client: Client, message: Message):
    match = message.matches[0]
    dx = match.group(1)
    global n, d, x
    if dx == "大":
        n = 1
        d += 1
        x = 0
    else:
        n = int(2 * n / 0.975) + 1
        d = 0
        x += 1
    r = None
    if d > 2:
        r = f"连续{d}次大"
    elif x > 2:
        r = f"连续{x}次小"

    await client.send_message(TARGET, "/ydx")
    if r:
        await client.send_message(-1002114116260, r)


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def get_redpocket_gen(client: Client, message: Message):
    for _ in range(n):
        await message.click(1, 4)
        # await asyncio.sleep(1)
