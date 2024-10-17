from pyrogram.types.messages_and_media import Message
from pyrogram.filters import create


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


async def choujiang_bot_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.is_bot and m.from_user.id == 6461022460)


choujiang_bot = create(choujiang_bot_filter)


async def zhuque_bot_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.is_bot and m.from_user.id == 5697370563)


zhuque_bot = create(zhuque_bot_filter)


async def auth_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.id == 5848633300)


auth = create(auth_filter)

async def yyz_bot_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.is_bot and m.from_user.id == 6296776523)


yyz_bot = create(yyz_bot_filter)

async def agsv_bot_filter(_, __, m: Message):
    return bool(m.from_user and m.from_user.is_bot and m.from_user.id == 6929566752)


agsv_bot = create(agsv_bot_filter)