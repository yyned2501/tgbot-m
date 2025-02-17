from pyrogram.types.messages_and_media import Message
from pyrogram.filters import create


def create_bot_filter(bot_id):
    async def bot_filter(_, __, m: Message):
        return bool(m.from_user and m.from_user.is_bot and m.from_user.id == bot_id)

    return create(bot_filter)


async def reply_to_me_filter(_, __, m: Message):
    return bool(
        m.reply_to_message
        and m.reply_to_message.from_user
        and m.reply_to_message.from_user.is_self
    )


reply_to_me = create(reply_to_me_filter)


async def command_to_me_filter(_, __, m: Message):
    return bool(
        m.reply_to_message
        and m.reply_to_message.reply_to_message
        and m.reply_to_message.reply_to_message.from_user
        and m.reply_to_message.reply_to_message.from_user.is_self
    )


command_to_me = create(command_to_me_filter)

choujiang_bot = create_bot_filter(6461022460)
zhuque_bot = create_bot_filter(5697370563)
yyz_bot = create_bot_filter(6296776523)
agsv_bot = create_bot_filter(6929566752)
ptvicomo_bot = create_bot_filter(7124396542)


async def auth_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.id == 5848633300)


auth = create(auth_filter)
