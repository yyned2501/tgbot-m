import json
import logging
import time
import traceback
from app import Client, redis_cli, scheduler

logger = logging.getLogger("main")
logger.info("启动定时删除消息任务")


async def s_delete_message(app: Client):
    # 获取所有以 "DM" 开头的键
    delete_messages_keys = redis_cli.keys("DM*")
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
