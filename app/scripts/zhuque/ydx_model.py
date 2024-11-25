import asyncio
import datetime

from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from sqlalchemy import desc, select

from app import app, logger, scheduler
from app.config import setting
from app.filters import custom_filters
from app.models import ASession
from app.models.ydx import YdxHistory, ZqYdx
from app.scripts.zhuque.ex.bet_modes import mode, get_funcs

TARGET = -1001833464786
rate = 0.99
dx_list = ["小", "大"]
bs_list = ["s", "b"]
ex_bet = {"bonus": 0, "win": 0, "lose": 0, "aim": 0, "win_bonus": 0}


def new_history_list(message: Message, data: list[int]):
    lines = message.text.strip().split("\n")
    single_line_list = []
    start = 0
    for line in lines[1:5]:
        line = line.strip("[]").split()
        line = [int(num) for num in line]
        single_line_list.extend(line)
    saved_index = len(single_line_list)
    if ld := len(data) < 40:
        start = saved_index - ld
    for i in range(start, saved_index):
        if (t := single_line_list[i:]) == data[: len(t)]:
            saved_index = i
            break
    save_list = single_line_list[:saved_index]
    save_list.reverse()
    logger.info(f"保存数据{save_list}")
    return save_list, single_line_list


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
                        await message.edit(f"兜底 {db.bet_round} 轮！！！！。。。")
                        await asyncio.sleep(5)
                        await message.delete()

                elif message.command[1] == "mbb":
                    if len(message.command) >= 3:
                        max_bet_bonus = message.command[2]
                        if max_bet_bonus.isdigit():
                            max_bet_bonus = int(max_bet_bonus)
                            if 500 <= max_bet_bonus <= 50000000:
                                db.max_bet_bonus = max_bet_bonus
                            else:
                                await message.edit(f"最大单次下注应在500-5000w内")
                                await asyncio.sleep(5)
                                await message.delete()
                                return
                        await message.edit(
                            f"最大下注 {db.max_bet_bonus} ！！！！。。。"
                        )
                        await asyncio.sleep(5)
                        await message.delete()
                elif message.command[1] == "mds":
                    funcs_dict = get_funcs()
                    r = (
                        "有以下模式可以选择：```\n"
                        + "\n".join([k for k in funcs_dict])
                        + "```"
                    )
                    await message.edit(r)
                    await asyncio.sleep(10)
                    await message.delete()
                elif message.command[1] == "exbet":
                    if len(message.command) >= 3:
                        global ex_bet
                        bonus = message.command[2]
                        try:
                            bonus = int(bonus)
                            ex_bet["bonus"] = bonus
                        except:
                            pass
                        if len(message.command) >= 4:
                            aim = message.command[3]
                            if aim.isdigit():
                                aim = int(aim)
                                ex_bet["aim"] = aim
                        if bonus > 0:
                            r = f"跟投 {bonus}"
                        elif bonus < 0:
                            r = f"反投 {-bonus}"
                        elif bonus == 0:
                            ex_bet = {
                                "bonus": 0,
                                "win": 0,
                                "lose": 0,
                                "aim": 0,
                                "win_bonus": 0,
                            }
                            r = "跟投停止"
                        await message.edit(f"{r} 净胜 {ex_bet['aim']} 次！！！。。。")
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
    global ex_bet
    async with ASession() as session:
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)
            dx = dx_list.index(Lottery_Point)

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
                if ex_bet.get("message_id"):
                    if ex_bet.get("message_id") == message.reply_to_message_id:
                        re_mess = "跟" if ex_bet["bonus"] > 0 else "反"
                        if (dx == db.dx and ex_bet["bonus"] > 0) or (
                            dx != db.dx and ex_bet["bonus"] < 0
                        ):
                            ex_bet["win"] += 1
                            re_mess = f"{re_mess}投胜"
                            ex_bet["win_bonus"] += abs(ex_bet["bonus"]) * 0.99
                        else:
                            ex_bet["lose"] += 1
                            re_mess = f"{re_mess}投负"
                            ex_bet["win_bonus"] -= abs(ex_bet["bonus"])
                        re_mess = f"**[ {re_mess} ]** {ex_bet["win"]}-{ex_bet["lose"]} 累计盈亏：{(ex_bet["win_bonus"]):.02f}"
                        if ex_bet["win"] - ex_bet["lose"] >= ex_bet["aim"]:
                            ex_bet = {
                                "bonus": 0,
                                "win": 0,
                                "lose": 0,
                                "aim": 0,
                                "win_bonus": 0,
                            }
                        await app.send_message(
                            setting["zhuque"]["ydx_model"]["push_chat_id"], re_mess
                        )
                    del ex_bet["message_id"]


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def zhuque_ydx_bet(client: Client, message: Message):
    async with ASession() as session:
        async with session.begin():
            history_result = await session.execute(
                select(YdxHistory).order_by(desc(YdxHistory.id)).limit(50)
            )
            history = history_result.scalars().all()
            save_list, data = new_history_list(
                message, [ydx_history.dx for ydx_history in history]
            )
            session.add_all([YdxHistory(dx=dx) for dx in save_list])
        await asyncio.sleep(5)
        async with session.begin():
            db = await session.get(ZqYdx, 1) or ZqYdx.init(session)
            # 保存新历史数据
            if db.bet_switch == 1:
                if db.message_id:
                    logger.warning("检测到上局未结束，5秒后重新检测...")
                    scheduler.add_job(
                        zhuque_ydx_bet,
                        "date",
                        next_run_time=datetime.datetime.now()
                        + datetime.timedelta(seconds=1),
                        args=(client, message),
                    )
                    return None
                db.message_id = message.id
                ex_bet["message_id"] = message.id
                # 按模式设置大小
                mode(db.bet_mode, db, data)

                # 计算下注金额
                remaining_bouns = int(db.sum_losebonus / rate) + db.start_bonus * (
                    db.lose_times + 1
                )
                if remaining_bouns >= db.max_bet_bonus + 500:
                    await app.send_message(TARGET, f"没兜住")
                    await db.set_start_bonus()
                    remaining_bouns = db.start_bonus
                    db.sum_losebonus = 0
                    db.lose_times = 0
                db.betbonus = remaining_bouns // 500 * 500
                # 对应按钮金额
                if ex_bet["bonus"] != 0:
                    remaining_bouns += ex_bet["bonus"]
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
                bet_dx = db.dx
                if remaining_bouns < 0:
                    remaining_bouns = -remaining_bouns
                    bet_dx = 1 - db.dx
                for value in bet_values:
                    count = remaining_bouns // value
                    bet_counts.append(count)
                    remaining_bouns -= count * value

                # 嵌套循环点击下注
                for i, count in enumerate(bet_counts):
                    if count > 0:
                        bet_value = bet_values[i]
                        callback_data = f'{{"t":"{bs_list[bet_dx]}","b":{
                            int(bet_value)},"action":"ydxxz"}}'
                        logger.info(
                            f"bet_value= {bet_value} count= {count} callback_data= {callback_data}"
                        )
                        for _ in range(count):
                            result_message = await app.request_callback_answer(
                                message.chat.id, message.id, callback_data
                            )
                            await asyncio.sleep(1)
                            if "零食不足" in result_message.message:
                                db.bet_switch = 0
                                logger.info(f"破产了")
                                await app.send_message(TARGET, f"破产了")
                                return
