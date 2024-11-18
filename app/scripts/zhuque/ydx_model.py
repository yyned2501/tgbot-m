import asyncio

from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from sqlalchemy import desc, select

from app import app, logger
from app.config import setting
from app.filters import custom_filters
from app.models import ASession
from app.models.ydx import YdxHistory, ZqYdx
from app.scripts.zhuque.ex.bet_modes import mode, test
from app.libs.zhuque_requests import get_info

TARGET = -1001833464786
rate = 0.99
dx_list = ["小", "大"]
bs_list = ["s", "b"]


@app.on_message(filters.command("zqydx") & filters.me)
async def zhuque_ydx_switch(client: Client, message: Message):
    async with ASession() as session:
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)
            if message.command[0] == "zqydx":
                if message.command[1] == "on":
                    db.bet_switch = 1
                    await message.edit(f"朱雀自动 “运动鞋” 穿起来。。。")
                    if db.message_id:
                        l_mess = await client.get_messages(
                            message.chat.id, db.message_id
                        )
                        if l_mess.empty or "已结算" in l_mess.text:
                            await message.edit(
                                f"朱雀自动 “运动鞋” 穿起来。。。\n上局对局已结束，自动重置"
                            )
                            db.high_times = 0
                            db.low_times = 0
                            db.betbonus = 0
                            db.lose_times = 0
                            db.win_times = 0
                            db.sum_losebonus = 0
                            db.message_id = None
                            db.dx = 1
                    await asyncio.sleep(5)
                    await message.delete()

                elif message.command[1] == "off":
                    db.bet_switch = 0
                    await message.edit(f"朱雀自动 “运动鞋” 脱掉！脱掉！。。。")
                    await asyncio.sleep(5)
                    await message.delete()

                elif message.command[1] == "bonus":
                    if len(message.command) >= 3:
                        bonus = message.command[2]
                        if bonus.isdigit():
                            bonus = int(bonus)
                            if 500 <= bonus < 100000:
                                db.start_bonus = bonus
                                db.bet_round = None
                                await message.edit(
                                    f"底注 {db.start_bonus} 设置成功！。。。"
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
                        db.bet_mode = message.command[2].upper()
                        await message.edit(f"mode {db.bet_mode} 启动！！！！。。。")
                        await asyncio.sleep(5)
                        await message.delete()

                elif message.command[1] == "round":
                    if len(message.command) >= 3:
                        bet_round = message.command[2]
                        if bet_round.isdigit():
                            bet_round = int(bet_round)
                            if 5 <= bet_round < 12:
                                db.bet_round = bet_round
                            else:
                                await message.edit(f"兜底轮次应在5-12次内")
                                await asyncio.sleep(5)
                                await message.delete()
                                return
                        await message.edit(f"兜底{db.bet_round} 轮！！！！。。。")
                        await asyncio.sleep(5)
                        await message.delete()

                elif message.command[1] == "test":
                    pass


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
            dx = dx_list.index(Lottery_Point)
            session.add(YdxHistory(dx=dx))

            if db.kp_switch == 1:
                await asyncio.sleep(1)
                await app.send_message(TARGET, f"/ydx")

            if db.bet_switch == 1:
                if db.message_id and message.reply_to_message_id:
                    if db.message_id != message.reply_to_message_id:
                        logger.warning("结算id与记录不一致，重置历史记录")
                        db.high_times = 0
                        db.low_times = 0
                        db.betbonus = 0
                        db.lose_times = 0
                        db.win_times = 0
                        db.sum_losebonus = 0
                        db.message_id = None
                if dx == 1:
                    db.high_times += 1
                    db.low_times = 0
                else:
                    db.high_times = 0
                    db.low_times += 1
                db.message_id = None
                re_mess = None
                if db.betbonus > 0:
                    if db.high_times >= 1:
                        re_mess = f"庄盘连 “大” **{db.high_times}** 次"
                    elif db.low_times >= 1:
                        re_mess = f"庄盘连 “小” **{db.low_times}** 次"
                    if dx == db.dx:
                        thisround_winbouns = db.betbonus * rate - db.sum_losebonus
                        db.sum_losebonus = 0
                        add_bet_times = db.lose_times + 1
                        db.win_times += 1
                        db.lose_times = 0
                        re_mess = f"**[ 胜 ]** 连胜:**[ {db.win_times} ]**, 下注:**[ {dx_list[db.dx]} ]** 金额 {db.betbonus} , 本次盈利: {db.betbonus * 0.99}, 本轮追投盈利: {thisround_winbouns} ,**[本轮共计追投 {add_bet_times} 次]** , [{re_mess}]"
                        logger.info(re_mess)
                        db.betbonus = 0
                        if db.bet_round:
                            await db.set_start_bonus()
                    else:
                        db.sum_losebonus += db.betbonus
                        db.lose_times += 1
                        db.win_times = 0
                        re_mess = f"**[ 负 ]** 连负:**[ {db.lose_times} ]**, 下注:**[ {dx_list[db.dx]} ]** 金额 {db.betbonus} , 本次亏损: {db.betbonus} , 本轮追投累计亏损 {db.sum_losebonus} , [{re_mess}]"
                        logger.info(re_mess)
                        db.betbonus = 0
                    await app.send_message(
                        setting["zhuque"]["ydx_model"]["push_chat_id"], re_mess
                    )
                else:
                    if db.bet_round:
                        await db.set_start_bonus()


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def zhuque_ydx_bet(client: Client, message: Message):
    async with ASession() as session:
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)

            if db.bet_switch == 1:
                if db.message_id:
                    logger.warning("检测到上局未结束，5秒后重新检测...")
                    await asyncio.sleep(5)
                    return await zhuque_ydx_bet(client, message)
                db.message_id = message.id
                history_result = await session.execute(
                    select(YdxHistory).order_by(desc(YdxHistory.id)).limit(50)
                )
                history = history_result.scalars().all()

                # 按模式设置大小
                mode(db.bet_mode, db, history)

                # 计算下注金额
                remaining_bouns = int(db.sum_losebonus / rate) + db.start_bonus * (
                    db.lose_times + 1
                )
                if (
                    remaining_bouns // setting["zhuque"]["ydx_model"]["max_bet_bonus"]
                    > 0
                ):
                    remaining_bouns = db.start_bonus
                    db.sum_losebonus = 0
                # 对应按钮金额
                bet_values = [
                    50000000,
                    5000000,
                    1000000,
                    250000,
                    50000,
                    20000,
                    2000,
                    500,
                ]
                bet_counts = []
                # 计算每个下注金额按钮点击次数
                logger.info(f"remaining_bouns= {remaining_bouns}")
                for value in bet_values:
                    count = remaining_bouns // value
                    bet_counts.append(count)
                    remaining_bouns -= count * value

                # 嵌套循环点击下注
                for i, count in enumerate(bet_counts):
                    if count > 0:
                        bet_value = bet_values[i]
                        callback_data = f'{{"t":"{bs_list[db.dx]}","b":{
                            int(bet_value)},"action":"ydxxz"}}'
                        logger.info(
                            f"bet_value= {bet_value} count= {count} callback_data= {callback_data}"
                        )
                        for _ in range(count):
                            result_message = await app.request_callback_answer(
                                message.chat.id, message.id, callback_data
                            )
                            db.betbonus += bet_value
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
