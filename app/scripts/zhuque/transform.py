from pyrogram import filters
from pyrogram.types.messages_and_media import Message

from app import app
from app.models import ASSession
from app.models.transform import User
from app.filters import custom_filters
from app.libs.messages import delete_message

TARGET = -1001833464786
SITE_NAME = "朱雀"


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & custom_filters.command_to_me
    & filters.regex(r"转账成功, 信息如下: \n.+ 转出 (\d+)\n")
)
async def transform_get(client, message: Message):
    ls = message.matches[0].group(1)
    transform_message = message.reply_to_message
    transform_user = transform_message.from_user
    username = f"{transform_user.first_name} {transform_user.last_name}"
    async with ASSession() as session:
        async with session.begin():
            user = await User.get(transform_user.id, username)
            await user.add_transform_record(SITE_NAME, int(ls))
            get_bonus = await user.get_bonus_get_sum_for_site(SITE_NAME)
            post_bonus = await user.get_bonus_post_sum_for_site(SITE_NAME)
            reply_message = (
                f"```\n感谢 {username} 大佬赠送 的 {ls} 灵石\n"
                f"大佬一共给小弟转了 {get_bonus} 灵石\n"
                f"小弟一共给大佬转了 {-post_bonus} 灵石\n"
                "```"
            )
            delete_message(await transform_message.reply(reply_message), 60)


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & custom_filters.reply_to_me
    & filters.regex(r"转账成功, 信息如下: \n.+ 转出 (\d+)\n")
)
async def transform_use(client, message: Message):
    ls = message.matches[0].group(1)
    transform_message = message.reply_to_message.reply_to_message
    transform_user = transform_message.from_user
    username = f"{transform_user.first_name} {transform_user.last_name}"
    async with ASSession() as session:
        async with session.begin():
            user = await User.get(transform_user.id, username)
            await user.add_transform_record(SITE_NAME, int(ls))
            get_bonus = await user.get_bonus_get_sum_for_site(SITE_NAME)
            reply_message = (
                f"```\n{username} 送你 {ls} 灵石 能不能让你叫我一声大佬？\n"
                f"我一共给你转了 {get_bonus} 灵石\n"
                "```"
            )
            delete_message(await transform_message.reply(reply_message), 60)
