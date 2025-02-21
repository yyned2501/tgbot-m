import asyncio
from random import randint
import re
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types.messages_and_media import Message

from app import Client, logger
from app.filters import custom_filters

GROUP = -1002119517619
BOT = 6121385204


@Client.on_message(
    filters.chat(GROUP)
    & custom_filters.create_bot_filter(BOT)
    & custom_filters.command_to_me
    & filters.regex(r"真遗憾.*获得\s+([\d\.]+)\s+个魔力")
)
async def dajie_win(client: Client, message: Message):
    match = message.matches[0]
    bonus = float(match.group(1))
    logger.info(f"猪猪被打劫，获得{bonus}魔力")
    await message.reply_to_message.reply(f"感谢大佬赠送的 {bonus} 魔力，爱你哟")


@Client.on_message(
    filters.chat(GROUP)
    & custom_filters.create_bot_filter(BOT)
    & custom_filters.command_to_me
    & filters.regex(
        r"你成功打劫了.*加倍羞辱了 (\d+) 次 扣除税 ([\d\.]+) 共获得 ([\d\.]+) 个魔力"
    )
)
async def dajie_win(client: Client, message: Message):
    match = message.matches[0]
    count = int(match.group(1))
    tax = float(match.group(2))
    bonus = float(match.group(3))
    logger.info(f"猪猪被打劫，失去{bonus+tax}魔力")
    await message.reply_to_message.reply(f"竟敢抢我魔力 {bonus+tax} ? 看我打劫回来！")
    await message.reply_to_message.reply(f"/dajie {count}")
