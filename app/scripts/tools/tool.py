import asyncio
import json
import re
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.models import ASession
from app.models.redpocket import Redpocket
from app.filters import custom_filters
from app.config import setting


@app.on_message(
    filters.command("getmessage") & filters.reply
)
async def get_message(client: Client, message: Message):
    with open("message.json","w") as f:
        f.write(str(message.reply_to_message))
    await client.send()
