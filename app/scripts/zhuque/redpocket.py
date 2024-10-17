import asyncio
import re
from random import randint
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from pyrogram.enums import ParseMode

from app import app, logger
from app.models import ASession
from app.models.redpocket import Redpocket
from app.filters import custom_filters
from app.config import setting


TARGET = -1001833464786

redpockets = {}


async def in_redpockets_filter(_, __, m: Message):
    return bool(m.text in redpockets)


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"点击领取红包")
)
async def get_redpocket_gen(client: Client, message: Message):
    return logger.info(await message.click(0))
