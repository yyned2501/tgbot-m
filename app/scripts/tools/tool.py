from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app


@app.on_message(filters.command("getmessage") & filters.reply)
async def get_message(client: Client, message: Message):
    with open("message.json", "w") as f:
        f.write(str(message.reply_to_message))
    await client.send()
