import datetime
import logging
import traceback
from pyrogram.types.messages_and_media import Message
from app import scheduler

logger = logging.getLogger("main")


async def _delete_message(message: Message):
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        traceback.print_exc()
        delete_message(message, 5)


def delete_message(message: Message, sleep_sec: int):
    scheduler.add_job(
        _delete_message,
        "date",
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=sleep_sec),
        args=(message,),
    )
