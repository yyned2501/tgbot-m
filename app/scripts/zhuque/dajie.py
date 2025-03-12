import asyncio
from pyrogram import filters
from pyrogram.types.messages_and_media import Message

from app import Client


TARGET = -1001833464786


@Client.on_message(filters.chat(TARGET) & filters.reply & filters.command("fdajie"))
async def fdajie(client: Client, message: Message):
    await message.delete()
    count = int(message.command[1])
    if len(message.command) > 2:
        new_name = message.command[2]
    first_name = client.me.first_name
    last_name = client.me.last_name
    await client.update_profile(new_name, "")
    r_message = await message.reply_to_message.reply(f"/dajie {count}")
    await asyncio.sleep(1)
    await r_message.delete()
    await client.update_profile(first_name, last_name)
