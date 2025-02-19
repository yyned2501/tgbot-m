import json
import logging
import time
import traceback
from pyrogram.types.messages_and_media import Message
from app import app, redis_cli, scheduler

logger = logging.getLogger("main")


def delete_message(message: Message, delay: int = 0):
    data = {
        "chatid": message.chat.id,
        "messageid": message.id,
        "deletetime": int(time.time()) + delay,
    }

    redis_cli.set(
        f"DM:{message.chat.id}:{message.id}",
        json.dumps(data),
    )


async def s_delete_message():
    # 获取所有以 "DM" 开头的键
    delete_messages_keys = redis_cli.keys("DM*")
    logger.info(f"待删除的消息列表{delete_messages_keys}")
    if delete_messages_keys:
        for key in delete_messages_keys:
            value = redis_cli.get(key)
            value_str: str = value.decode("utf-8")
            data: dict[str, int] = json.loads(value_str)
            chatid = data.get("chatid")
            messageid = data.get("messageid")
            deletetime = data.get("deletetime")
            if deletetime:
                # 检查是否到了删除时间
                if deletetime <= time.time():
                    try:
                        # 尝试删除消息
                        await app.delete_messages(chatid, messageid)
                        redis_cli.delete(key)
                    except Exception as e:
                        # 捕获异常并记录错误信息
                        traceback.print_exc()
                        logger.error(f"Error deleting message: {e}")


scheduler.add_job(s_delete_message, "interval", seconds=1)
logger.info(f"当前任务列表: {scheduler.get_jobs()}")
