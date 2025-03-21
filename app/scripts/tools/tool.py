import asyncio
import logging
import contextlib

from pyrogram import filters
import pyrogram
from pyrogram.types.messages_and_media import Message
from pyrogram.raw.functions import photos

from app import Client
from app.libs.messages import delete_message

logger = logging.getLogger("main")
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


@Client.on_message(filters.command("getmessage") & filters.reply)
async def get_message(client: Client, message: Message):
    with open("message.json", "w") as f:
        f.write(str(message.reply_to_message))
    await client.send_document("me", "message.json")


@Client.on_message(filters.command("setloglevel"))
async def set_log_level(client: Client, message: Message):
    level = message.command[1].upper()
    if level in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[level])
        await message.edit(f"已将日志调整为{level}")
    await asyncio.sleep(5)
    await message.delete()


async def self_delatemessage(client: Client, message: Message):
    """Deletes specific amount of messages you sent."""
    msgs = []
    count_buffer = 0
    offset = 0
    if len(message.command) != 2:
        if not message.reply_to_message:
            return await message.edit(f"命令格式不对请输入/dme number")
        offset = message.reply_to_message.id
    try:
        count = int(message.command[1])
        await message.delete()
    except ValueError:
        await message.edit(f"删除数量错误 请输出正整数")
        return

    async for msg in client.search_messages(
        message.chat.id, from_user="me", limit=count
    ):
        count_buffer += 1
        msgs.append(msg.id)

    if msgs:
        await client.delete_messages(message.chat.id, msgs)

    delete_message(
        await client.send_message(
            message.chat.id, f"已删除消息{str(count_buffer)} / {str(count)}"
        ),
        3,
    )


@Client.on_message(filters.me & filters.command("dme"))
async def call_self_delatemessage(client: Client, message: Message):
    await self_delatemessage(client, message)


@Client.on_message(filters.me & filters.command("lphoto"))
async def lphoto(client: Client, message: Message):
    photos_list = []
    async for photo in client.get_chat_photos("me"):
        photo_path = await client.download_media(photo.file_id)

    await message.edit("正在发送头像...")
    for photo_path in photos_list:
        await client.send_document("me", photo)

    await message.edit("所有头像已发送到你的私聊。")


@Client.on_message(filters.me & filters.command("gphoto") & filters.reply)
async def gphoto(client: Client, message: Message):
    async for photo in client.get_chat_photos(message.reply_to_message.from_user.id, 1):
        await client.download_media(photo.file_id, file_name="photo.jpg")
    await message.edit("已获取目标用户头像")


@Client.on_message(filters.me & filters.command("sphoto"))
async def sphoto(client: Client, message: Message):
    await client.set_profile_photo(photo="downloads/photo.jpg")
    await message.delete()


@Client.on_message(filters.me & filters.command("rphoto"))
async def rphoto(client: Client, message: Message):
    async for photo in client.get_chat_photos("me", 1):
        await client.delete_profile_photos(photo.file_id)
    await message.edit("已恢复头像")


@Client.on_message(filters.me & filters.command("dphoto"))
async def dphoto(client: Client, message: Message):
    n = 0
    async for photo in client.get_chat_photos("me"):
        if n == 0:
            n += 1
            continue
        await client.delete_profile_photos(photo.file_id)
    await message.delete()
