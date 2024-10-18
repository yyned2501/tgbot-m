import json
import random
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.filters import custom_filters


TARGET = -1001833464786

n = 1
d = 0
x = 0
ldx = 0


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"已结算: 结果为 \d (.)")
)
async def get_redpocket_gen(client: Client, message: Message):
    match = message.matches[0]
    dx = match.group(1)
    global n, d, x, ldx
    if dx == ldx:
        n = 1
    else:
        n = int(2 * n / 0.995) + 1
    if dx == "大":
        d += 1
        x = 0
    else:
        d = 0
        x += 1
    r = None
    if d > 1:
        r = f"连续{d}次大"
    elif x > 1:
        r = f"连续{x}次小"

    if r:
        await client.send_message(-1002114116260, r)


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def get_redpocket_gen(client: Client, message: Message):
    d = random.randint(0, 1)
    global ldx
    ldx = "大" if d == 1 else "小"
    for _ in range(n):
        await message.click(d, 4)


@app.on_message(filters.command("request") & filters.reply)
async def get_redpocket_gen(client: Client, message: Message):
    data = '{"t":"b","b":50000,"action":"ydxxz"}'
    # str_data = json.dumps(data)
    logger.info(data)
    await client.request_callback_answer(
        message.reply_to_message.chat.id, message.reply_to_message_id, data
    )


@app.on_message(filters.command("message") & filters.reply)
async def get_redpocket_gen(client: Client, message: Message):
    print(message)
