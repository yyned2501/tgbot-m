import datetime
from random import randint
from pyrogram.types.messages_and_media import Message
from pyrogram import filters, Client
from sqlalchemy import select

from app import app
from app.models import ASSession
from app.models.redpocket import Transform

TARGET = -1002022762746


@app.on_message(
    filters.chat(TARGET) & filters.regex(r"^#小萝莉给点"),
)
async def gift(client: Client, message: Message):
    session = ASSession()
    today_midnight = datetime.datetime.combine(
        datetime.datetime.today().date(), datetime.datetime.min.time()
    )
    if message.from_user:
        uid = message.from_user.id
    else:
        return
    async with session.begin():
        today_tranform = (
            (
                await session.execute(
                    select(Transform).filter(
                        Transform.create_time >= today_midnight,
                        Transform.site == "象站",
                        Transform.bonus < 0,
                    )
                )
            )
            .scalars()
            .all()
        )
        uids = [tr.user_id for tr in today_tranform]
        if len(uids) < 50:
            if uid in uids:
                await message.reply(f"今天给过了，明天再来！")
            else:
                bonus = randint(5, 1000)
                session.add(Transform(site="象站", user_id=uid, bonus=-bonus))
                await message.reply(f"+{bonus}")
