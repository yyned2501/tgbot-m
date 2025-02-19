import json
import logging
import time
from pyrogram.types.messages_and_media import Message
from app import redis_cli

logger = logging.getLogger("main")


def delete_message(message: Message, delay: int = 0):
    logger.info(f"添加删除任务DM:{message.chat.id}:{message.id}")
    data = {
        "chatid": message.chat.id,
        "messageid": message.id,
        "deletetime": int(time.time()) + delay,
    }
    redis_cli.set(
        f"DM:{message.chat.id}:{message.id}",
        json.dumps(data),
    )
    delete_messages_keys = redis_cli.keys("DM*")
    logger.info(f"待删除的消息列表{delete_messages_keys}")
