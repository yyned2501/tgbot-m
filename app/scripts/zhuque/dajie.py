import asyncio
from pyrogram import filters
from pyrogram.types.messages_and_media import Message

from app import Client
import os


TARGET = -1001833464786
BOT_ID = 5697370563


@Client.on_message(
    filters.chat(TARGET) & filters.reply & filters.me & filters.command("fdajie")
)
async def fdajie(client: Client, message: Message):
    count = int(message.command[1])
    if len(message.command) > 2:
        new_first_name = message.command[2]
        new_last_name = message.command[3] if len(message.command) > 3 else ""
    else:
        new_first_name = message.reply_to_message.from_user.first_name
        new_last_name = message.reply_to_message.from_user.last_name
    reply_message_id = message.reply_to_message.id
    await message.delete()
    if not os.path.exists("downloads/photo.jpg"):  # 下载头像
        async for photo in client.get_chat_photos(BOT_ID, 1):
            await client.download_media(photo.file_id, file_name="photo.jpg")
    first_name = client.me.first_name
    last_name = client.me.last_name
    await client.update_profile(new_first_name, new_last_name)  # 更新名字
    await client.set_profile_photo(photo="downloads/photo.jpg")  # 更新头像
    r_message = await client.send_message(
        TARGET, f"/dajie {count}", reply_to_message_id=reply_message_id
    )

    await asyncio.sleep(1)
    await r_message.delete()
    await client.update_profile(first_name, last_name)  # 恢复名字
    async for photo in client.get_chat_photos("me", 1):
        await client.delete_profile_photos(photo.file_id)  # 删除头像

@app.on_message(
    filters.chat(TARGET) & filters.reply & filters.me & filters.command("fdajie")
)
async def fdajie(client: Client, message: Message):
    count = int(message.command[1])
    if len(message.command) > 2:
        new_first_name = message.command[2]
        new_last_name = message.command[3] if len(message.command) > 3 else ""
    else:
        new_first_name = message.reply_to_message.from_user.first_name
        new_last_name = message.reply_to_message.from_user.last_name
    reply_message_id = message.reply_to_message.id
    await message.delete()
    if not os.path.exists("downloads/photo.jpg"):  # 下载头像
        async for photo in client.get_chat_photos(BOT_ID, 1):
            await client.download_media(photo.file_id, file_name="photo.jpg")
    if not os.path.exists("downloads/me.jpg"):  # 下载头像
        async for photo in client.get_chat_photos("me", 1):
            await client.download_media(photo.file_id, file_name="me.jpg")
    first_name = client.me.first_name
    last_name = client.me.last_name
    await client.update_profile(new_first_name, new_last_name)  # 更新名字
    await client.set_profile_photo(photo="downloads/photo.jpg")  # 更新头像
    r_message = await client.send_message(
        TARGET, f"/dajie {count}", reply_to_message_id=reply_message_id
    )

    await asyncio.sleep(1)
    await r_message.delete()
    await client.update_profile(first_name, last_name)  # 恢复名字
    await client.set_profile_photo(photo="downloads/me.jpg")  # 更新头像
