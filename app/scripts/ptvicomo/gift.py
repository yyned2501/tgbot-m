import datetime
from random import randint
from pyrogram.types.messages_and_media import Message
from pyrogram import filters, Client
from sqlalchemy import select

from app import app
from app.models import ASSession
from app.models.transform import Transform, User
from app.libs.messages import delete_message

TARGET = -1002022762746


@app.on_message(
    filters.chat(TARGET) & filters.regex(r"^#小萝莉给点"),
)
async def gift(client: Client, message: Message):

    today_midnight = datetime.datetime.combine(
        datetime.datetime.today().date(), datetime.datetime.min.time()
    )
    async with ASSession() as session:
        async with session.begin():
            user = await User.get(message.from_user)
            async with session.begin_nested():
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
                    if user.id in uids:
                        delete_message(
                            await message.reply(f"今天给过了，明天再来！"), 30
                        )
                    else:
                        bonus = randint(100, 1000)
                        await user.add_transform_record("象站", bonus)
                        await message.reply(f"+{bonus}")
