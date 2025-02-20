from pyrogram.types.messages_and_media import Message

from app.models import ASSession
from app.models.transform import User
from app.libs.messages import delete_message


async def transform(transform_message: Message, bonus: int, site: str, bonus_name: str):
    transform_user = transform_message.from_user
    async with ASSession() as session:
        async with session.begin():
            user = await User.get(transform_user)
            await user.add_transform_record(site, bonus)
            get_bonus = await user.get_bonus_get_sum_for_site(site)
            post_bonus = await user.get_bonus_post_sum_for_site(site)
            if bonus > 0:
                reply_message = (
                    f"```\n感谢 {user.name} 大佬赠送的 {bonus} {bonus_name}\n"
                    f"大佬一共给小弟转了 {get_bonus} {bonus_name}\n"
                    f"小弟一共给大佬转了 {post_bonus} {bonus_name}\n"
                    "```"
                )
            else:
                reply_message = (
                    f"```\n小{user.name}, 送你 {-bonus} {bonus_name} 能不能让你叫我一声大佬？\n"
                    f"我一共给你转了 {post_bonus} {bonus_name}\n"
                    "```"
                )
            delete_message(await transform_message.reply(reply_message), 60)
