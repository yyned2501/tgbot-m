
import asyncio
import random
import re
from app import app, logger
from app.config import setting
from app.filters import custom_filters
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message

TARGET = -1001833464786
start_bouns = 500
bet_bouns = 0
high_times = 0
low_times = 0
bet_point = 0
bet_switch = 0
bet_mode = 'A'
kp_switch = 0
rele_betbouns = 0
lose_times =  0
win_times = 0
sum_losebouns = 0
add_bet_times = 0
last_bet_point = '小'
last_flag = 's'

@app.on_message(filters.chat(TARGET) 
                & filters.command("zqydx")             
                &filters.me
                )
async def zhuque_ydx_switch(client: Client, message: Message): 
    global kp_switch,bet_switch,bet_mode,start_bouns
    if message.command[0] == "zqydx":
        if message.command[1] == "on":
            bet_switch = 1
            await message.edit(f"朱雀自动 “运动鞋” 穿起来。。。")
            await asyncio.sleep(5)
            await message.delete()

        elif message.command[1] == "on":
            bet_switch = 0
            await message.edit(f"朱雀自动 “运动鞋” 脱掉！脱掉！。。。")
            await asyncio.sleep(5)
            await message.delete()

        elif message.command[1] == "set":
            if len(message.command) >= 3:
                if message.command[2].isdigit():
                    if (int(message.command[1]) < 100000
                        and int(message.command[1]) >= 500):
                        start_bouns = int(message.command[1])
                        await message.edit(f"底注 {start_bouns} 设置成功！。。。")
                        await asyncio.sleep(5)
                        await message.delete()

        elif message.command[1] == "kp":
            if len(message.command) >= 3:
                if message.command[2] == 'on':
                    kp_switch = 1
                    await message.edit(f"自动开盘启动！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()
                elif message.command[2] == 'on':
                    kp_switch = 0
                    await message.edit(f"自动开盘关闭！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()
        elif message.command[1] == "md":

            if len(message.command) >= 3:
                if message.command[2] == 'a':
                    bet_mode = 'A'
                    await message.edit(f"mode A 启动！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()
                elif message.command[2] == 'b':
                    bet_mode = 'B'
                    await message.edit(f"mode A 启动！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()
                elif message.command[2] == 'c':
                    bet_mode = 'C'
                    await message.edit(f"mode c 启动！！！！。。。")
                    await asyncio.sleep(5)
                    await message.delete()
                elif message.command[2] == 'd':
                    bet_mode = 'D'
                    await message.edit(f"mode c 启动！！！！。。。")
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
    global bet_bouns, high_times, low_times, bet_point, bet_switch,bet_mode,rele_betbouns,my_username,lose_times,win_times,sum_losebouns,add_bet_times,kp_switch
      
    
    if bet_switch == 1:
        
        if bet_point != 0:
            if Lottery_Point == bet_point:
                bet_bouns = start_bouns
                thisround_winbouns = rele_betbouns * 0.99 - sum_losebouns
                sum_losebouns = 0
                add_bet_times = lose_times + 1
                win_times += 1
                lose_times = 0
            else:
                bet_bouns = int(2 * bet_bouns / 0.95) + start_bouns
                sum_losebouns += rele_betbouns
                lose_times += 1
                win_times = 0
                add_bet_times = 0

        if Lottery_Point == "大":
            high_times += 1
            low_times = 0
        else:
            high_times = 0
            low_times += 1
        re_message = None
        if high_times >= 1:
            re_message = f"庄盘已连续开 “大” {high_times} 次"
        elif low_times >= 1:
            re_message = f"庄盘已连续开 “小” {low_times} 次"  

        win_check = await listofWinners_check(message, setting['tg']['username'])
        if win_check:
            re_mess= f"**[胜]** 本次实际下注 {rele_betbouns} , 本次投注盈利: {rele_betbouns * 0.99}, **连续判胜: {win_times} 次**, 本轮追投盈利: {thisround_winbouns} ,**[本轮共计追投 {add_bet_times} 次]** , **[{re_message}]**"
            logger.info(re_mess)            
            rele_betbouns = 0
            await app.send_message(setting['GB_VAR']['GROUP_ID']['PRIVATE_ID'],re_mess)
        else:
            re_mess = f"**[负]** 本次实际下注 {rele_betbouns} , 本次投注亏损: {rele_betbouns} , **连续判负: {lose_times} 次**, 本轮追投累计亏损 {sum_losebouns} , **[{re_message}]**"
            logger.info(re_mess)
            rele_betbouns = 0
            await app.send_message(setting['GB_VAR']['GROUP_ID']['PRIVATE_ID'],re_mess)
        if kp_switch == 1:
            await app.send_message(TARGET,f"/ydx")    




@app.on_message(
    filters.chat(TARGET) & custom_filters.zhuque_bot & filters.regex(r"创建时间")
)
async def zhuque_ydx_bet(client: Client, message: Message):

    global bet_point,bet_bouns,bet_switch,bet_mode,rele_betbouns,flag,last_bet_point,last_flag
    
    
    if bet_switch == 1:
        if bet_mode == 'A':   #追大
            bet_point="大"
            flag = "b"

        elif bet_mode == 'B': #追小
            bet_point="小"
            flag = "s"


        elif bet_mode == 'C': #启动时追小，连败3败后追上次胜局，连败后3次后继续切上次胜的
            if lose_times > 2:
                if flag == "s":
                    bet_point="大"
                    flag = "b"
                    
                else:
                    bet_point="小"
                    flag = "s"

            else:
                bet_point = last_bet_point
                flag = last_flag

        elif bet_mode == 'D':
            if random.random() <= 0.5:
                bet_point="大"
                flag = "b"
            else:
                bet_point="小"
                flag = "s"

        last_bet_point = bet_point
        last_flag = flag
        # 计算下注金额
        if bet_bouns == 0:
            bet_bouns = start_bouns
            
        if bet_bouns //  5000000 > 1:
            bet_bouns = start_bouns
        # 对应按钮金额
        bet_values = [1000000, 250000, 50000, 20000, 5000, 2000, 500]
        bet_counts = []
        # 计算每个下注金额按钮点击次数
        remaining_bouns = bet_bouns 
        logger.info(f"remaining_bouns= {remaining_bouns}")       
        for value in bet_values:
            count = remaining_bouns // value
            bet_counts.append(count)
            remaining_bouns -= count * value
        
        # 嵌套循环点击下注
        for i, count in enumerate(bet_counts):
            if count > 0:
                bet_value = bet_values[i]
                callback_data = f'{{"t":"{flag}","b":{int(bet_value)},"action":"ydxxz"}}'
                logger.info(f"bet_value= {bet_value} count= {count} callback_data= {callback_data}")
                for _ in range(count):
                    result_message = await app.request_callback_answer(message.chat.id, message.id,callback_data)
                    rele_betbouns += bet_value
                    await asyncio.sleep(1)
                    if "零食不足" in result_message.message:
                        bet_switch = 0
                        logger.info(f"破产了")
                        await app.send_message(TARGET,f"破产了")
                        return

async def listofWinners_check(message: Message, target_username: str) -> bool:
    for entity in message.entities:
        if entity.user:
            if entity.user.username == target_username:                
                return True   
    return False
