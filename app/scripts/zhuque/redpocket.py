import asyncio
import json
import re
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.filters import custom_filters


TARGET = -1001833464786

redpockets = {}


async def in_redpockets_filter(_, __, m: Message):
    return bool(m.text in redpockets)


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"内容: (.*)\n灵石: .*\n剩余: .*\n大善人: (.*)")
)
async def get_redpocket_gen(client: Client, message: Message):
    match = message.matches[0]
    from_user = match.group(2)
    
    while True:
        button_reply = await message.click(0)
        reply_dict = json.loads(str(button_reply))
        if m:=reply_dict.get("message"):
            if m in ["已领完","不能重复领取"]:
                return
            match = re.search(r"已获得 (\d+) 灵石", m)
            if match:
                bonus = match.group(1)
                return await client.send_message(
                    TARGET, f"感谢大善人 {from_user} 的红包~\n感谢 {bonus} 零食的打赏~"
                )
        await asyncio.sleep(1)


@app.on_message(filters.me & filters.command("message") & filters.reply)
async def getmessage(client: Client, message: Message):
    await message.delete()
    logger.info(str(message.reply_to_message.text))
