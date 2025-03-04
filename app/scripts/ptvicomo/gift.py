import datetime
from random import randint
from pyrogram.types.messages_and_media import Message
from pyrogram import filters
from sqlalchemy import select

from app import Client, setting
from app.models import ASSession
from app.models.transform import Transform, User
from app.libs.messages import delete_message

TARGET = -1002022762746
SITE_NAME = "象岛"


@Client.on_message(
    filters.chat(TARGET) & filters.regex(rf"^{setting["ptvicomo"]["gift"]["keyword"]}"),
)
async def gift(client: Client, message: Message):
    today_midnight = datetime.datetime.combine(
        datetime.datetime.today().date(), datetime.datetime.min.time()
    ).astimezone(datetime.timezone.utc)
    async with ASSession() as session:
        async with session.begin():
            user = await User.get(message.from_user)
            today_tranform = (
                (
                    await session.execute(
                        select(Transform).filter(
                            Transform.create_time >= today_midnight,
                            Transform.site == SITE_NAME,
                            Transform.bonus < 0,
                        )
                    )
                )
                .scalars()
                .all()
            )
            uids = set([tr.user_id for tr in today_tranform])
            if len(uids) < setting["ptvicomo"]["gift"]["count"]:
                if user.id in uids:
                    delete_message(await message.reply(f"今天给过了，明天再来！"), 30)
                else:
                    bonus = randint(100, 1000)
                    await message.reply(f"+{bonus}")
