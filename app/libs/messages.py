import datetime
import logging
import traceback
from pyrogram.types.messages_and_media import Message
from app import scheduler

logger = logging.getLogger("main")


async def _delete_message(message: Message):
    logger.info(f"删除消息{message.text}")
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        traceback.print_exc()
        delete_message(message, 5)


def delete_message(message: Message, sleep_sec: int):
    next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=sleep_sec)
    logger.info(f"添加定时删除消息{message.text}，删除时间{next_run_time}")
    scheduler.add_job(
        _delete_message,
        "date",
        next_run_time=next_run_time,
        args=(message,),
    )
    logger.info(f"当前任务列表: {scheduler.get_jobs()}")
