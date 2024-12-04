import asyncio
import datetime

from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from sqlalchemy import desc, select, update

from app import app, logger, scheduler
from app.config import setting
from app.filters import custom_filters
from app.models import ASSession
from app.models.ydx import YdxHistory, ZqYdxBase, ZqYdxMulti
from app.scripts.zhuque.ex.bet_modes import mode, test

TARGET = -1001833464786
rate = 0.99
dx_list = ["小", "大"]
bs_list = ["s", "b"]
ex_bet = {"bonus": 0, "win": 0, "lose": 0, "aim": 0, "win_bonus": 0, "betbonus": 0}


async def new_history_list(message: Message):
    """
    通过秋人提供的40个数据来生成历史数据列表

    Args:
        message (Message): tgmessage
        data (list[int]): 已有的历史数据

    Returns:
        single_line_list(list[int]): 最后40个数据用于预测
    """
    lines = message.text.strip().split("\n")
    single_line_list = []
    start = 0
    for line in lines[1:5]:
        line = line.strip("[]").split()
        line = [int(num) for num in line]
        single_line_list.extend(line)
    session = ASSession()
    async with session.begin():
        history_result = await session.execute(
            select(YdxHistory).order_by(desc(YdxHistory.id)).limit(40)
        )
        history = history_result.scalars().all()
        last_saved_time = history[0].create_time
        if datetime.datetime.now() - last_saved_time > datetime.timedelta(minutes=1):
            data = [ydx_history.dx for ydx_history in history]
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
            if len(save_list) > 0:
                session.add_all([YdxHistory(dx=dx) for dx in save_list])
        else:
            logger.error(
                "记录上次记录时间与当前时间小于1分钟，防止数据错误，不记录数据。"
            )
    return single_line_list


async def ydx(client: Client, message: Message, bonus: int):
    """
    获取当前用户在指定站点的bonus总和。

    :param client: pyrogram app对象
    :param message: pyrogram message对象
    :param bonus: 下注金额正数大，负数小
    """

    bet_dx = 1
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

    logger.info(f"remaining_bouns= {bonus}")
    if bonus < 0:
        bonus = -bonus
        bet_dx = 1 - bet_dx
    for value in bet_values:
        count = bonus // value
        bet_counts.append(count)
        bonus -= count * value

    for i, count in enumerate(bet_counts):
        if count > 0:
            bet_value = bet_values[i]
            callback_data = f'{{"t":"{bs_list[bet_dx]}","b":{
                int(bet_value)},"action":"ydxxz"}}'
            logger.info(
                f"bet_value= {bet_value} count= {count} callback_data= {callback_data}"
            )
            for _ in range(count):
                await client.request_callback_answer(
                    message.chat.id, message.id, callback_data
                )
                await asyncio.sleep(1)


@app.on_message(filters.command("zqydx") & filters.me)
async def zhuque_ydx_switch(client: Client, message: Message):
    session = ASSession()
    async with session.begin():
        base = await session.get(ZqYdxBase, 1) or ZqYdxBase.init()
        if message.command[1] == "on":
            await message.edit(f"朱雀自动 “运动鞋” 穿起来。。。")
            base.bet_switch = 1
            if base.message_id:
                l_mess = await client.get_messages(message.chat.id, base.message_id)
                if l_mess.empty or "已结算" in l_mess.text:
                    await message.edit(
                        f"朱雀自动 “运动鞋” 穿起来。。。\n上局对局已结束，自动重置"
                    )
                    base.message_id = None
                    await session.execute(
                        update(ZqYdxMulti).values(lose_times=0, sum_losebonus=0)
                    )
            await asyncio.sleep(5)
            await message.delete()

        elif message.command[1] == "off":
            base.bet_switch = 0
            await message.edit(f"朱雀自动 “运动鞋” 脱掉！脱掉！。。。")
            await asyncio.sleep(5)
            await message.delete()

        elif message.command[1] == "bonus":
            if len(message.command) >= 3:
                bonus = message.command[2]
                if bonus.isdigit():
                    bonus = int(bonus)
                    if 500 <= bonus < 100000:
                        base.start_bonus = bonus
                        base.bet_round = None
                        await message.edit(f"底注 {base.start_bonus} 设置成功！。。。")
                        await asyncio.sleep(5)
                        await message.delete()

        elif message.command[1] == "kp":
            if len(message.command) >= 3:
                if message.command[2] == "on":
                    base.kp_switch = 1
                    await message.edit(f"自动开盘启动！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()
                elif message.command[2] == "off":
                    base.kp_switch = 0
                    await message.edit(f"自动开盘关闭！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()

        elif message.command[1] == "round":
            if len(message.command) >= 3:
                bet_round = message.command[2]
                if bet_round.isdigit():
                    bet_round = int(bet_round)
                    if 5 <= bet_round < 12:
                        base.bet_round = bet_round
                    else:
                        await message.edit(f"兜底轮次应在5-12次内")
                        await asyncio.sleep(5)
                        await message.delete()
                        return
                await message.edit(f"兜底 {base.bet_round} 轮！！！！。。。")
                await asyncio.sleep(5)
                await message.delete()

        elif message.command[1] == "mbb":
            if len(message.command) >= 3:
                max_bet_bonus = message.command[2]
                if max_bet_bonus.isdigit():
                    max_bet_bonus = int(max_bet_bonus)
                    if 500 <= max_bet_bonus <= 50000000:
                        base.max_bet_bonus = max_bet_bonus
                    else:
                        await message.edit(f"最大单次下注应在500-5000w内")
                        await asyncio.sleep(5)
                        await message.delete()
                        return
                await message.edit(f"最大下注 {base.max_bet_bonus} ！！！！。。。")
                await asyncio.sleep(5)
                await message.delete()

        elif message.command[1] == "mdtest":
            if len(message.command) >= 3:
                count = int(message.command[2])
                await message.edit("测试中...")
                history_result = await session.execute(
                    select(YdxHistory).order_by(desc(YdxHistory.id)).limit(count + 40)
                )
                history = history_result.scalars().all()
                data = [ydx_history.dx for ydx_history in history]
                models = test(base, data)
                r = f"```测试{count}次模型：\n"
                for k in models:
                    r += f"模型{k}:\n历史失败次数:{models[k]["loss_count"]}\n最大失败轮次:{models[k]["max_nonzero_index"]}\n净胜次数:{models[k]["win_count"]}\n胜率:{models[k]["win_rate"]:.02%}\n当前失败轮次:{models[k]["turn_loss_count"]}\n模型预测:{models[k]["guess"]}\n\n"
                r += "```"
                await message.edit(r)
                await asyncio.sleep(30)
                await message.delete()

        elif message.command[1] == "models":
            # if len(message.command) == 2:
            models = await session.execute(select(ZqYdxMulti))
            r = f"**所有运行模型转态**："
            for model in models.scalars():
                r += f"\n{"[**ON**]" if model.bet_switch == 1 else "[OFF]"}模型{model.model_name}"
                if model.fit_model == "D":
                    r += f"[倍投]\n当前连败次数:{model.lose_times}|累计下注金额:{model.sum_losebonus}|累计盈利:{model.win_bonus}"
                elif model.fit_model == "+":
                    r += f"[跟投]\n胜:{model.win}|负:{model.lose}|累计盈利:{model.win_bonus}"
                elif model.fit_model == "-":
                    r += f"[反投]\n胜:{model.win}|负:{model.lose}|累计盈利:{model.win_bonus}"
                r += "\n"
            await message.edit(r[:-1])
            await asyncio.sleep(30)
            await message.delete()


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def zhuque_ydx_bet(client: Client, message: Message):
    await new_history_list(message)