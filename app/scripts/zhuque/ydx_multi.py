import asyncio
import datetime

from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from sqlalchemy import desc, or_, select, update

from app import app, logger, scheduler
from app.config import setting
from app.filters import custom_filters
from app.models import ASSession
from app.models.ydx import YdxHistory, ZqYdxBase, ZqYdxMulti
from app.scripts.zhuque.ex.bet_modes_multi import mode, test, get_funcs

TARGET = -1001833464786
rate = 0.99
dx_list = ["小", "大"]
bs_list = ["s", "b"]
ex_bet = {"bonus": 0, "win": 0, "lose": 0, "aim": 0, "win_bonus": 0, "betbonus": 0}
fit_model_name = {"G": "网格", "D": "倍投", "+": "跟投", "-": "反投"}
grids = [0]
for i in range(1, 30):
    last_g = grids[i - 1]
    grids.append(max(last_g / 0.99 + int(i / 10) + 1, last_g / 0.9))


def delete_message(message: Message, sleep_sec: int):
    async def _delete_message(message: Message):
        await message.delete()

    scheduler.add_job(
        _delete_message,
        "date",
        next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=sleep_sec),
        args=(message,),
    )


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
    single_line_list.reverse()
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

    logger.info(f"下注{bonus}")
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
            logger.debug(
                f"bet_value= {bet_value} count= {count} callback_data= {callback_data}"
            )
            for _ in range(count):
                await client.request_callback_answer(
                    message.chat.id, message.id, callback_data
                )
                await asyncio.sleep(1)


async def check_ydx_message(message: Message, base: ZqYdxBase):
    session = ASSession()
    if base.message_id and message.reply_to_message_id:
        if base.message_id != message.reply_to_message_id:
            logger.warning("结算id与记录不一致，重置历史记录")
            await session.execute(
                update(ZqYdxMulti).values(
                    bet_bonus=0, winning_streak=0, losing_streak=0, sum_losebonus=0
                )
            )


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
                        update(ZqYdxMulti).values(
                            bet_bonus=0,
                            winning_streak=0,
                            losing_streak=0,
                            sum_losebonus=0,
                        )
                    )
            await asyncio.sleep(5)
            await message.delete()

        elif message.command[1] == "off":
            base.bet_switch = 0
            await message.edit(f"朱雀自动 “运动鞋” 脱掉！脱掉！。。。")
            delete_message(message, 5)

        elif message.command[1] == "bonus":
            if len(message.command) >= 3:
                bonus = message.command[2]
                if bonus.isdigit():
                    bonus = int(bonus)
                    if 500 <= bonus < 100000:
                        base.start_bonus = bonus
                        base.bet_round = None
                        await message.edit(f"底注 {base.start_bonus} 设置成功！。。。")
                        delete_message(message, 5)

        elif message.command[1] == "kp":
            if len(message.command) >= 3:
                if message.command[2] == "on":
                    base.kp_switch = 1
                    await message.edit(f"自动开盘启动！！！！。。。")
                    delete_message(message, 5)
                elif message.command[2] == "off":
                    base.kp_switch = 0
                    await message.edit(f"自动开盘关闭！！！！。。。")
                    delete_message(message, 5)

        elif message.command[1] == "round":
            if len(message.command) >= 3:
                bet_round = message.command[2]
                if bet_round.isdigit():
                    bet_round = int(bet_round)
                    if 5 <= bet_round < 12:
                        base.bet_round = bet_round
                    else:
                        await message.edit(f"兜底轮次应在5-12次内")
                        delete_message(message, 5)
                        return
                await message.edit(f"兜底 {base.bet_round} 轮！！！！。。。")
                delete_message(message, 5)

        elif message.command[1] == "mbb":
            if len(message.command) >= 3:
                max_bet_bonus = message.command[2]
                if max_bet_bonus.isdigit():
                    max_bet_bonus = int(max_bet_bonus)
                    if 500 <= max_bet_bonus <= 50000000:
                        base.max_bet_bonus = max_bet_bonus
                    else:
                        await message.edit(f"最大单次下注应在500-5000w内")
                        delete_message(message, 5)
                        return
                await message.edit(f"最大下注 {base.max_bet_bonus} ！！！！。。。")
                delete_message(message, 5)

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
                dx_guess = []
                r = f"```测试{count}次模型：\n"
                for k in models:
                    dx_guess.append(
                        models[k]["win_rate"]
                        if models[k]["guess"] == 1
                        else 1 - models[k]["win_rate"]
                    )
                    r += f"模型{k}:\n历史失败次数:{models[k]["loss_count"]}\n最大失败轮次:{models[k]["max_nonzero_index"]}\n净胜次数:{models[k]["win_count"]}\n胜率:{models[k]["win_rate"]:.02%}\n当前失败轮次:{models[k]["turn_loss_count"]}\n模型预测:{models[k]["guess"]}\n\n"
                r += f"模型综合预测:{sum(dx_guess)/len(dx_guess):.02%} 概率 大"
                r += "```"
                await message.edit(r)
                delete_message(message, 30)

        elif message.command[1] == "models":
            if len(message.command) == 2:
                models = await session.execute(select(ZqYdxMulti))
                r = f"**所有运行模型转态**："
                for model in models.scalars():
                    r += f"\n{"[**ON**]" if model.bet_switch == 1 else "[OFF]"}模型{model.name}"
                    if model.fit_model == "D":
                        r += f"[倍投]\n当前连败次数:{model.losing_streak}|本次下注金额:{model.bet_bonus}|累计盈利:{model.win_bonus}"
                    elif model.fit_model == "G":
                        r += f"[网格]\n当前网格:{model.lose-model.win}|本次下注金额:{model.bet_bonus}|累计盈利:{model.win_bonus}"
                    elif model.fit_model == "+":
                        r += f"[跟投]\n胜:{model.win}|负:{model.lose}|本次下注金额:{model.bet_bonus}|累计盈利:{model.win_bonus}"
                    elif model.fit_model == "-":
                        r += f"[反投]\n胜:{model.win}|负:{model.lose}|本次下注金额:{model.bet_bonus}|累计盈利:{model.win_bonus}"
                    r += "\n"
                await message.edit(r[:-1])
                delete_message(message, 5)
            else:
                """
                /zqydx models a on
                /zqydx models a off
                /zqydx models a d
                /zqydx models a +100000
                /zqydx models a -100000
                /zqydx models a clear
                """
                if len(message.command) == 4:
                    model_name = message.command[2].upper()
                    command = message.command[3].upper()
                    funcs = get_funcs()
                    if model_name in funcs:
                        model = (
                            await session.execute(
                                select(ZqYdxMulti).where(ZqYdxMulti.name == model_name)
                            )
                        ).scalar_one()
                        if command == "ON":
                            model.bet_switch = 1
                            model.losing_streak = 0
                            model.winning_streak = 0
                            model.bet_bonus = 0
                            model.sum_losebonus = 0
                            await message.edit(f"模型{model.name}启动")
                        elif command == "OFF":
                            model.bet_switch = 0
                            await message.edit(f"模型{model.name}停止")
                        elif command == "CLEAR":
                            model.lose = 0
                            model.win = 0
                            model.losing_streak = 0
                            model.winning_streak = 0
                            model.bet_bonus = 0
                            model.sum_losebonus = 0
                            model.win_bonus = 0
                            await message.edit(f"模型{model.name}清理历史数据")
                        elif command == "D":
                            model.fit_model = command
                            model.losing_streak = 0
                            model.winning_streak = 0
                            model.bet_bonus = 0
                            model.sum_losebonus = 0
                            await message.edit(f"模型{model.name}修改为倍投模式")
                        elif command == "G":
                            model.fit_model = command
                            model.lose = 3
                            model.win = 0
                            await message.edit(f"模型{model.name}修改为网格模式")
                        elif command[0] == "+" or command[0] == "-":
                            bonus = int(command[1:])
                            model.fit_model = command[0]
                            model.bonus = bonus
                            await message.edit(
                                f"模型{model.name}修改为{"跟" if command[0] == "+" else "反"}投{model.bonus}模式"
                            )
                    delete_message(message, 5)


@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def zhuque_ydx_bet(client: Client, message: Message):
    data = await new_history_list(message)
    session = ASSession()
    error = 0
    while error < 5:
        await asyncio.sleep(5)
        async with session.begin():
            base = await session.get(ZqYdxBase, 1) or ZqYdxBase.init(session)
            if base.bet_switch == 0:
                return
            if not base.message_id:
                bet_bonus_sum = 0
                # 倍投下注
                running_d_models = await session.execute(
                    select(ZqYdxMulti).filter(
                        ZqYdxMulti.bet_switch == 1, ZqYdxMulti.fit_model == "D"
                    )
                )
                running_d_models_list = running_d_models.scalars().all()
                running_d_models_count = len(running_d_models_list)
                for model in running_d_models_list:
                    if model.losing_streak > base.bet_round + 1:
                        model.bet_switch = 0
                        model.losing_streak = 0
                        model.winning_streak = 0
                        model.bet_bonus = 0
                        model.sum_losebonus = 0
                        await client.send_message(
                            TARGET,
                            f"模型{model.name}没兜住，自动停止，损失{model.sum_losebonus}",
                        )
                    else:
                        dx = mode(model.name, data)
                        if model.losing_streak > 7:
                            delete_message(
                                await client.send_message(
                                    TARGET,
                                    f"滴滴滴！模型{model.name}连负[{model.losing_streak}]，模型预测{dx}",
                                ),
                                60,
                            )
                        if model.losing_streak == 0:
                            model.bonus = int(base.start_bonus / running_d_models_count)
                        bet_bonus = int(
                            model.sum_losebonus / 0.99
                            + (model.losing_streak + 1) * model.bonus
                        )
                        model.bet_bonus = (2 * dx - 1) * bet_bonus
                        bet_bonus_sum += model.bet_bonus
                # 网格下注
                running_g_models = await session.execute(
                    select(ZqYdxMulti).filter(
                        ZqYdxMulti.bet_switch == 1, ZqYdxMulti.fit_model == "G"
                    )
                )
                running_g_models_list = running_g_models.scalars().all()
                running_g_models_count = len(running_g_models_list)
                for model in running_g_models_list:
                    dx = mode(model.name, data)
                    if model.losing_streak > 7:
                        delete_message(
                            await client.send_message(
                                TARGET,
                                f"滴滴滴！模型{model.name}连负[{model.losing_streak}]，模型预测{dx}",
                            ),
                            60,
                        )
                    new_bonus = int(
                        min(
                            base.start_bonus * 4 / running_g_models_count,
                            base.start_bonus * 2,
                        )
                    )
                    if model.sum_losebonus > 0:
                        model.bonus = max(new_bonus, model.bonus)
                    else:
                        model.bonus = new_bonus
                    bet_bonus = int(
                        grids[min(model.lose - model.win, 29)] * model.bonus
                    )
                    model.bet_bonus = (2 * dx - 1) * bet_bonus
                    bet_bonus_sum += model.bet_bonus
                # 跟投下注
                running_ex_models = await session.execute(
                    select(ZqYdxMulti).filter(
                        ZqYdxMulti.bet_switch == 1,
                        or_(ZqYdxMulti.fit_model == "+", ZqYdxMulti.fit_model == "-"),
                    )
                )
                for model in running_ex_models.scalars():
                    dx = mode(model.name, data)
                    if model.fit_model == "-":
                        dx = 1 - dx
                    model.bet_bonus = (2 * dx - 1) * model.bonus
                    bet_bonus_sum += model.bet_bonus
                await ydx(client, message, bet_bonus_sum)
                base.message_id = message.id
                return
            else:
                logger.warning("检测到上局未结束，5秒后重新检测...")
                error += 1


@app.on_message(
    filters.chat(TARGET)
    & custom_filters.zhuque_bot
    & filters.regex(r"已结算: 结果为 \d (.)")
)
async def zhuque_ydx_check(client: Client, message: Message):
    match = message.matches[0]
    dx = dx_list.index(match.group(1))
    session = ASSession()
    res_mess = None
    async with session.begin():
        base = await session.get(ZqYdxBase, 1) or ZqYdxBase.init(session)
        if base.kp_switch == 1:
            await app.send_message(TARGET, f"/ydx")
        if base.message_id:
            await check_ydx_message(message, base)
        base.message_id = None
        models = await session.execute(
            select(ZqYdxMulti).filter(ZqYdxMulti.bet_bonus != 0)
        )
        res_mess = ""
        for model in models.scalars():
            if model.bet_bonus * (2 * dx - 1) > 0:
                model.win += 1
                model.winning_streak += 1
                model.losing_streak = 0
                model.sum_losebonus = (
                    0
                    if model.fit_model == "D"
                    else model.sum_losebonus - int(abs(model.bet_bonus) * 0.99)
                )
                model.win_bonus += int(abs(model.bet_bonus) * 0.99)
                r = f"[胜{model.winning_streak}]"
            else:
                model.lose += 1
                model.losing_streak += 1
                model.winning_streak = 0
                model.sum_losebonus += abs(model.bet_bonus)
                model.win_bonus -= abs(model.bet_bonus)
                r = f"[负{model.losing_streak}]"
            r += f"[{fit_model_name[model.fit_model]}]"
            r += f"[{model.win}-{model.lose}] 模型 {model.name} : 下注 {model.bet_bonus} 累计盈亏：{model.win_bonus}\n"
            if model.fit_model == "G":
                if model.lose <= model.win:
                    model.fit_model = "D"
            if model.fit_model == "D":
                if (model.losing_streak == 0) and (model.lose - model.win >= 10):
                    model.fit_model = "G"
                    model.lose = 3
                    model.win = 0
            res_mess += r
            model.bet_bonus = 0
            if model.bet_switch == 0:
                model.losing_streak = 0
                model.winning_streak = 0
                model.sum_losebonus = 0
    if res_mess:
        await app.send_message(setting["zhuque"]["ydx_model"]["push_chat_id"], res_mess)
        async with session.begin():
            base = await session.get(ZqYdxBase, 1) or ZqYdxBase.init(session)
            if base.bet_switch and base.bet_round:
                await base.set_start_bonus()
