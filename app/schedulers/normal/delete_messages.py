import json
import logging
import time
import traceback
from app import app, redis_cli, scheduler

logger = logging.getLogger("main")
logger.info("启动定时删除消息任务")


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
for job in scheduler.get_jobs():
    logger.info(f"Job {job.id} next run time: {job.next_run_time}")
