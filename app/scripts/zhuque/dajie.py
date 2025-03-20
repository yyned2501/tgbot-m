import asyncio
from pyrogram import filters
from pyrogram.types.messages_and_media import Message

from app import Client


TARGET = -1001833464786


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
    first_name = client.me.first_name
    last_name = client.me.last_name
    await client.update_profile(new_first_name, new_last_name)
    r_message = await client.send_message(
        TARGET, f"/dajie {count}", reply_to_message_id=reply_message_id
    )
    await asyncio.sleep(1)
    await r_message.delete()
    await client.update_profile(first_name, last_name)
