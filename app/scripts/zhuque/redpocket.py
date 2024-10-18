import asyncio
import json
import re
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.models import ASession
from app.models.redpocket import Redpocket
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
    content = match.group(1)
    from_user = match.group(2)

    while True:
        button_reply = await message.click(0)
        if m := button_reply.message:
            if m in ["已领完", "不能重复领取"]:
                return
            match = re.search(r"已获得 (\d+) 灵石", m)
            if match:
                bonus = match.group(1)

                async with ASession() as session:
                    async with session.begin():
                        redpocket = await Redpocket.add("zhuque", bonus, session)
                        ret_str = f"""```红包 {content} 领取成功
成功领取口令红包 {bonus} 灵石
今日领取口令红包 {redpocket.today_bonus} 灵石
累计领取口令红包 {redpocket.total_bonus} 灵石```"""
                        await client.send_message("me", ret_str)
                return
        await asyncio.sleep(1)


@app.on_message(filters.me & filters.command("message") & filters.reply)
async def getmessage(client: Client, message: Message):
    await message.delete()
    logger.info(str(message.reply_to_message.text))

@app.on_message(filters.me & filters.command("add2"))
async def getmessage(client: Client, message: Message):
    async with ASession() as session:
        async with session.begin():
            redpocket = await Redpocket.add("zhuque", 1, session)
            ret_str = f"""```红包 1 领取成功
成功领取口令红包 1 灵石
今日领取口令红包 {redpocket.today_bonus} 灵石
累计领取口令红包 {redpocket.total_bonus} 灵石```"""
            await client.send_message("me", ret_str)
