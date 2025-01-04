import asyncio
from random import randint, sample
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from app.filters import custom_filters
from app import app

TARGET = -1002022762746


@app.on_message(
    filters.chat(
        TARGET) & custom_filters.ptvicomo_bot & filters.regex(r"奖池金额"),
)
async def lottery(client: Client, message: Message):
    numbers_all = list(range(10))
    for _ in range(3):
        number = list(map(str, sample(numbers_all, 3)))
        bonus = randint(10000, 100000)
        await message.reply(f"{"".join(number)}*{bonus}")
        await asyncio.sleep(1)
