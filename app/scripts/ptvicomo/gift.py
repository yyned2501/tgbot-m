import datetime
from random import randint
from pyrogram.types.messages_and_media import Message
from pyrogram import filters, Client
from sqlalchemy import select

from app import app
from app.models import ASSession
from app.models.redpocket import Transform, User
from app.libs.messages import delete_message

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
        name = [message.from_user.first_name, message.from_user.last_name]
        name = " ".join([n for n in name if n])
    else:
        return
    async with session.begin():
        if user := await session.get(User, uid):
            if user.name != name:
                user.name = name
        else:
            session.add(
                User(
                    id=uid,
                    name=name,
                )
            )
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
                delete_message(await message.reply(f"今天给过了，明天再来！"), 30)
            else:
                bonus = randint(100, 1000)
                session.add(Transform(site="象站", user_id=uid, bonus=-bonus))
                await message.reply(f"+{bonus}")
