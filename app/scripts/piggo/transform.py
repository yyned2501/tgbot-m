from pyrogram import filters
from pyrogram.types.messages_and_media import Message

from app import Client
from app.filters import custom_filters
from app.libs.transform import transform

GROUP = -1002119517619
BOT = 6121385204
SITE_NAME = "猪猪"
BONUS_NAME = "魔力"


@Client.on_message(
    filters.chat(GROUP)
    & custom_filters.create_bot_filter(BOT)
    & custom_filters.command_to_me
    & filters.regex(r"转账成功！.*你已扣除含手续共 (\d+) 魔力")
)
async def transform_get(client, message: Message):
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message
    return await transform(transform_message, int(bonus), SITE_NAME, BONUS_NAME)


@Client.on_message(
    filters.chat(GROUP)
    & custom_filters.create_bot_filter(BOT)
    & custom_filters.reply_to_me
    & filters.regex(r"转账成功！.*你已扣除含手续共 (\d+) 魔力")
)
async def transform_use(client, message: Message):
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message.reply_to_message
    return await transform(transform_message, -int(bonus), SITE_NAME, BONUS_NAME)
