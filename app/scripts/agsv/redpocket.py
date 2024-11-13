import asyncio
from random import randint
from pyrogram.types.messages_and_media import Message
from pyrogram import filters, Client
from pyrogram.enums import ParseMode

from app import app, logger
from app.filters.custom_filters import agsv_bot
from app.config import setting

TARGET = -1002123701097


@app.on_message(filters.chat(TARGET) & agsv_bot & filters.regex(r"幸运抽奖"))
async def get_redpocket_message(client: Client, message: Message):
    await asyncio.sleep(randint(5, 10))
    logger.info("AGSV:参与幸运抽奖")
    try:
        await message.click(0)
    except:
        pass
    await client.send_message(
        setting["agsv"]["redpocket"]["push_chat_id"], "AGSV:参与幸运抽奖"
    )


@app.on_message(filters.chat(TARGET) & agsv_bot & filters.regex(r"领取口令: (.+)$"))
async def get_redpocket_message(client: Client, message: Message):
    await asyncio.sleep(randint(5, 10))
    kl = message.matches[0].group(1)
    logger.info(f"AGSV:领取口令红包{kl}")
    await client.send_message(
        message.chat.id, f"{message.matches[0].group(1)}", ParseMode.DISABLED
    )
    await client.send_message(
        setting["agsv"]["redpocket"]["push_chat_id"], f"AGSV:领取口令红包{kl}"
    )


@app.on_message(filters.chat(TARGET) & agsv_bot & filters.regex(r"^【.+红包】"))
async def get_redpocket_message(client: Client, message: Message):
    await asyncio.sleep(randint(5, 10))
    logger.info(f"AGSV:领取普通红包")
    try:
        await message.click(0)
    except:
        pass
    await client.send_message(
        setting["agsv"]["redpocket"]["push_chat_id"], f"AGSV:领取普通红包"
    )
