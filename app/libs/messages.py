import datetime
from pyrogram.types.messages_and_media import Message
from app import scheduler


async def _delete_message(message: Message):
    await message.delete()


def delete_message(message: Message, sleep_sec: int):
    scheduler.add_job(
        _delete_message,
        "date",
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=sleep_sec),
        args=(message,),
    )
