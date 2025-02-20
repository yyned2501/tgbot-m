from pyrogram import filters
from pyrogram.types.messages_and_media import Message

from app import Client
from app.filters import custom_filters
from app.libs.transform import transform

TARGET = [-1002022762746]
SITE_NAME = "象岛"
BONUS_NAME = "象草"


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.ptvicomo_bot
    & custom_filters.command_to_me
    & filters.regex(r"给 .+ 发送了 (\d+) 象草\n")
)
async def transform_get(client, message: Message):
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message
    return await transform(transform_message, int(bonus), SITE_NAME, BONUS_NAME)


@Client.on_message(
    filters.chat(TARGET)
    & custom_filters.ptvicomo_bot
    & custom_filters.reply_to_me
    & filters.regex(r"给 .+ 发送了 (\d+) 象草\n")
)
async def transform_use(client, message: Message):
    bonus = message.matches[0].group(1)
    transform_message = message.reply_to_message.reply_to_message
    return await transform(transform_message, -int(bonus), SITE_NAME, BONUS_NAME)
