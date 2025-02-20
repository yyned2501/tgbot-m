import asyncio
from random import randint
from pyrogram.types.messages_and_media import Message
from pyrogram import filters

from app import Client, logger
from app.filters import custom_filters


TARGET = -1001873711923


@Client.on_message(
    filters.chat(TARGET)
    & filters.inline_keyboard
    & custom_filters.yyz_bot
    & filters.regex(r"红包\d+号"),
)
async def click_redpocket(client: Client, message: Message):
    await asyncio.sleep(randint(2, 10))
    logger.info("redleaves:参与普通红包")
    try:
        await message.click(0)
    except:
        pass
