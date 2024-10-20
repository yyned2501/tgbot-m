import asyncio
import random

from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

from app import app, logger
from app.config import setting
from app.filters import custom_filters
from app.models import ASession
from app.models.ydx import ZqYdx


TARGET = -1001833464786


@app.on_message(filters.chat(TARGET) & filters.command("zqydx") & filters.me)
async def zhuque_ydx_switch(client: Client, message: Message):
    async with ASession() as session:
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)
            if message.command[0] == "zqydx":
                if message.command[1] == "on":
                    db.bet_switch = 1
                    await message.edit(f"朱雀自动 “运动鞋” 穿起来。。。")
                    await asyncio.sleep(5)
                    await message.delete()

                elif message.command[1] == "on":
                    db.bet_switch = 0
                    await message.edit(f"朱雀自动 “运动鞋” 脱掉！脱掉！。。。")
                    await asyncio.sleep(5)
                    await message.delete()

                elif message.command[1] == "set":
                    if len(message.command) >= 3:
                        bonus = message.command[2]
                        if bonus.isdigit():
                            bonus = int(bonus)
                            if 500 <= bonus < 100000:
                                db.start_bouns = bonus
                                await message.edit(
                                    f"底注 {db.start_bouns} 设置成功！。。。"
                                )
                                await asyncio.sleep(5)
                                await message.delete()

                elif message.command[1] == "kp":
                    if len(message.command) >= 3:
                        if message.command[2] == "on":
                            db.kp_switch = 1
                            await message.edit(f"自动开盘启动！！！！。。。")
                            await asyncio.sleep(5)
                            await message.delete()
                        elif message.command[2] == "off":
                            db.kp_switch = 0
                            await message.edit(f"自动开盘关闭！！！！。。。")
                            await asyncio.sleep(5)
                            await message.delete()
                elif message.command[1] == "md":

                    if len(message.command) >= 3:
                        if message.command[2] == "a":
                            db.bet_mode = "A"
                            await message.edit(f"mode A 启动！！！！。。。")
                            await asyncio.sleep(5)
                            await message.delete()
                        elif message.command[2] == "b":
                            db.bet_mode = "B"
                            await message.edit(f"mode A 启动！！！！。。。")
                            await asyncio.sleep(5)
                            await message.delete()
                        elif message.command[2] == "c":
                            db.bet_mode = "C"
                            await message.edit(f"mode c 启动！！！！。。。")
                            await asyncio.sleep(5)
                            await message.delete()
                        elif message.command[2] == "d":
                            db.bet_mode = "D"
                            await message.edit(f"mode d 启动！！！！。。。")
                            await asyncio.sleep(5)
                            await message.delete()


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"已结算: 结果为 \d (.)")
)
async def zhuque_ydx_check(client: Client, message: Message):
    match = message.matches[0]
    Lottery_Point = match.group(1)
    async with ASession() as session:
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)
            if db.bet_switch == 1:
                if db.bet_point != "":
                    if Lottery_Point == db.bet_point:
                        thisround_winbouns = db.rele_betbouns * 0.99 - db.sum_losebouns
                        db.sum_losebouns = 0
                        db.add_bet_times = db.lose_times + 1
                        db.win_times += 1
                        db.lose_times = 0
                    else:
                        db.sum_losebouns += db.rele_betbouns
                        db.lose_times += 1
                        db.win_times = 0
                        db.add_bet_times = 0

                if Lottery_Point == "大":
                    db.high_times += 1
                    db.low_times = 0
                else:
                    db.high_times = 0
                    db.low_times += 1
                re_message = None
                if db.high_times >= 1:
                    re_message = f"庄盘连 “大” **{db.high_times}** 次"
                elif db.low_times >= 1:
                    re_message = f"庄盘连 “小” **{db.low_times}** 次"

                win_check = await listofWinners_check(
                    message, setting["tg"]["username"]
                )
                if win_check:
                    re_mess = f"**[ 胜 ]** 连胜:**[ {db.win_times} ]**, 下注:**[ {db.bet_point} ]** 金额 {db.rele_betbouns} , 本次盈利: {db.rele_betbouns * 0.99}, 本轮追投盈利: {thisround_winbouns} ,**[本轮共计追投 {db.add_bet_times} 次]** , [{re_message}]"
                    logger.info(re_mess)
                    db.rele_betbouns = 0
                    await app.send_message(
                        setting["GB_VAR"]["GROUP_ID"]["PRIVATE_ID"], re_mess
                    )
                else:
                    re_mess = f"**[ 负 ]** 连负:**[ {db.lose_times} ]**, 下注:**[ {db.bet_point} ]** 金额 {db.rele_betbouns} , 本次亏损: {db.rele_betbouns} , 本轮追投累计亏损 {db.sum_losebouns} , [{re_message}]"
                    logger.info(re_mess)
                    db.rele_betbouns = 0
                    await app.send_message(
                        setting["GB_VAR"]["GROUP_ID"]["PRIVATE_ID"], re_mess
                    )
                if db.kp_switch == 1:
                    await app.send_message(TARGET, f"/ydx")


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def zhuque_ydx_bet(client: Client, message: Message):

    async with ASession() as session:
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)
            flag = db.last_flag
            if db.bet_switch == 1:
                db.message_id = message.id
                if db.bet_mode == "A":  # 追大
                    db.bet_point = "大"
                    flag = "b"

                elif db.bet_mode == "B":  # 追小
                    db.bet_point = "小"
                    flag = "s"

                elif (
                    db.bet_mode == "C"
                ):  # 启动时追小，连败3败后追上次胜局，连败后3次后继续切上次胜的
                    if db.lose_times != 0:
                        if db.lose_times % 2 == 0:
                            if flag == "s":
                                db.bet_point = "大"
                                flag = "b"
                            else:
                                db.bet_point = "小"
                                flag = "s"
                        else:
                            db.bet_point = db.last_bet_point
                            flag = db.last_flag
                    else:
                        db.bet_point = db.last_bet_point
                        flag = db.last_flag

                elif db.bet_mode == "D":
                    if random.random() <= 0.5:
                        db.bet_point = "大"
                        flag = "b"
                    else:
                        db.bet_point = "小"
                        flag = "s"

                db.last_bet_point = db.bet_point
                db.last_flag = flag
                # 计算下注金额
                bet_bonus = int(db.sum_losebouns / 0.99) + db.start_bouns * (
                    db.lose_times + 1
                )
                if bet_bonus == 0:
                    bet_bonus = db.start_bouns

                if bet_bonus // 5000000 > 1:
                    bet_bonus = db.start_bouns
                # 对应按钮金额
                bet_values = [1000000, 250000, 50000, 20000, 5000, 2000, 500]
                bet_counts = []
                # 计算每个下注金额按钮点击次数
                if bet_bonus > 5000000:
                    remaining_bouns = 5000000
                else:
                    remaining_bouns = bet_bonus
                logger.info(f"remaining_bouns= {remaining_bouns}")
                for value in bet_values:
                    count = remaining_bouns // value
                    bet_counts.append(count)
                    remaining_bouns -= count * value

                # 嵌套循环点击下注
                for i, count in enumerate(bet_counts):
                    if count > 0:
                        bet_value = bet_values[i]
                        callback_data = f'{{"t":"{flag}","b":{
                            int(bet_value)},"action":"ydxxz"}}'
                        logger.info(
                            f"bet_value= {bet_value} count= {count} callback_data= {callback_data}"
                        )
                        for _ in range(count):
                            result_message = await app.request_callback_answer(
                                message.chat.id, message.id, callback_data
                            )
                            db.rele_betbouns += bet_value
                            await asyncio.sleep(1)
                            if "零食不足" in result_message.message:
                                db.bet_switch = 0
                                logger.info(f"破产了")
                                await app.send_message(TARGET, f"破产了")
                                return


async def listofWinners_check(message: Message, target_username: str) -> bool:
    for entity in message.entities:
        if entity.user:
            if entity.user.username == target_username:
                return True
    return False
