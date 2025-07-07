import asyncio
from app import app
import re
from pyrogram import filters, Client
from pyrogram.types.messages_and_media import Message
from filters import custom_filters
from reply_message import heimu_REPLY_MESSAGE,Sticker_REPLY_MESSAGE,noautolottery_REPLY_MESSAGE
from config import GROUP_ID,my_id,auto_choujiang,target_group,my_ptid,prize_list,start_time1,start_time2, end_time1,end_time2
from random import randint,random
from datetime import datetime
from libs import others
from app import logger


lottery_list = {}

#################抽奖监听#######################
@app.on_message(
    (custom_filters.choujiang_bot
    | custom_filters.test)
    & filters.regex(r"^新的抽奖已经创建[\s\S]+参与关键词：「(.+)」")
    )
async def lottery_forword_message(client:Client, message:Message):
    lottery_info = {}
    nowtime =await others.get_nowtime('time')
    start_time1_1 = datetime.strptime(start_time1, '%H:%M:%S%z')
    start_time2_1 = datetime.strptime(start_time2, '%H:%M:%S%z')
    end_time1_1 = datetime.strptime(end_time1, '%H:%M:%S%z')
    end_time2_1 = datetime.strptime(end_time2, '%H:%M:%S%z')
    
    pattern = {"ID": r"抽奖 ID：(.+)",
               "boss_name": r"创建者：(\w+)",
               "boss_ID": r"创建者：\w+\s+\((\d+)\)",
               "prize": r"奖品：\n      ▸ (.+)",
               "allowuser": r"允许普通用户参加：(.+)",
               "keyword": r"参与关键词：「(.+)」",
               }                
    for key, pat in pattern.items():
        match = re.search(pat, message.text)
        lottery_info[key] = match.group(1) if match else ""
    result_key= await prize_check(lottery_info["prize"])


    if auto_choujiang:
        if ((nowtime > start_time1_1.time()
             and nowtime < start_time2_1.time())
             or (nowtime > end_time1_1.time()
                 and nowtime < end_time2_1.time())):            
            if message.chat.id in target_group: 
                if result_key:
                    logger.info(f"自动抽奖已经打开,且符合自动抽奖时间,且属于目标群组范围，且奖品符合设定范围 开始自动抽奖 抽奖ID: {lottery_info['ID']}")
                    lottery_list[lottery_info['ID']] = {'keyword':lottery_info['keyword'],'boss_name':lottery_info['boss_name'],'boss_ID':lottery_info['boss_ID'],'ptsite':result_key,'prizechat':message.chat.id,'flag':0}
                    await asyncio.sleep(randint(25, 65)) 
                    if lottery_info['ID'] in lottery_list:                                                
                        logger.info(f"ID: {lottery_info['ID']}的抽奖,随机等待后未结束，故参与抽奖,参与群组:{message.chat.id},抽奖关键字:{lottery_list[lottery_info['ID']]['keyword']}")
                        re_message = await app.send_message(message.chat.id, lottery_list[lottery_info['ID']]['keyword'])
                        lottery_list[lottery_info['ID']]['flag'] = 1
                        await others.sendmessage(GROUP_ID["PRIVATE_ID"],f"ID: {lottery_info['ID']}的抽奖 \n参与群组:{message.chat.id},\n抽奖关键字:{lottery_list[lottery_info['ID']]['keyword']} \n成功参与抽奖 \n 抽奖链接：{message.link}")
                    else:
                        await others.sendmessage(GROUP_ID["PRIVATE_ID"],f"该抽奖在随机等待时间内已经结束，故不参与抽奖。 \n\n{message.text}\n\n{message.link}")
                        logger.info(f"ID: {lottery_info['ID']}的抽奖，在随机等待时间内已经结束，故不参与抽奖")
                else:
                    await others.sendmessage(GROUP_ID["PRIVATE_ID"],f"该抽奖奖品不符合设定范围故不参与抽奖 \n\n{message.text}\n\n{message.link}")
                    logger.info(f"抽奖ID: {lottery_info['ID']} 其奖品不符合设定范围故不参与抽奖 ")
            else:
                await others.sendmessage(GROUP_ID["PRIVATE_ID"],f"该抽奖所在群组不属于设定的目标群组范围,故不参与抽奖 \n\n{message.text}\n\n{message.link}")
                logger.info(f"抽奖ID: {lottery_info['ID']} 所在群组不属于设定的目标群组范围,故不参与抽奖")
        else:
            await others.sendmessage(GROUP_ID["PRIVATE_ID"],f"不在设定自动抽奖时间内,故不参与抽奖 \n\n{message.text}\n\n{message.link}")
            logger.info(f"抽奖ID: {lottery_info['ID']} 不在设定自动抽奖时间内,故不参与抽奖。")
    else:
        await others.sendmessage(GROUP_ID["PRIVATE_ID"],f"自动抽奖使能开关未打开,故不参与抽奖 \n\n{message.text}\n\n{message.link}")
        logger.info(f"抽奖ID: {lottery_info['ID']} 自动抽奖使能开关未打开,故不参与抽奖。")


#################中奖结果监听#######################
@app.on_message(
        filters.regex(r"^参与人数够啦！！开奖[\s\S]+中奖信息\n([\s\S]+)")
        & (custom_filters.choujiang_bot
           | custom_filters.test)   
    )
async def lottery_forword_message(client:Client, message:Message):
    finish_key = ""
    winner = message.matches[0].group(1)
    logger.info(f"lottery_list befor = {lottery_list} ")
    if auto_choujiang:
        if message.chat.id in target_group:
            match1 = re.search(r"抽奖 ID：(.+)", message.text)
            finish_key = match1.group(1) if match1 else ""
            if str(my_id) != str(lottery_list[finish_key]['boss_ID']):
                logger.info(f"抽奖不是自己发起的，未中奖随机发黑幕,中奖也自动领奖")
                if str(my_id) in winner:                
                    await asyncio.sleep(randint(15, 50)) 
                    if (lottery_list[finish_key]['ptsite'] == "ZHUQUE_ID"
                        or lottery_list[finish_key]['ptsite'] == "DOLBY_ID"
                        or lottery_list[finish_key]['ptsite'] == 'SSD_ID'
                        or lottery_list[finish_key]['ptsite'] == 'AUDIENCES_ID'):
                        if random() > 0.7:
                            re_message1 = await app.send_message(message.chat.id,f"感谢{lottery_list[finish_key]['boss_name']}大佬")
                        else:
                            await app.send_sticker(message.chat.id, Sticker_REPLY_MESSAGE[f"thank{randint(1,5)}"])

                        if message.chat.id != GROUP_ID[f"{lottery_list[finish_key]['ptsite']}"]:
                            if random()<0.3:
                                re_message2 = await app.send_message(GROUP_ID[f"{lottery_list[finish_key]['ptsite']}"],f"感谢{lottery_list[finish_key]['boss_name']} 爷 小弟在这")
                            elif random()>0.7:
                                re_message2 = await app.send_message(GROUP_ID[f"{lottery_list[finish_key]['ptsite']}"],f"{lottery_list[finish_key]['boss_name']}爷 射这里")
                            else:
                                re_message2 = await app.send_message(GROUP_ID[f"{lottery_list[finish_key]['ptsite']}"],f"{lottery_list[finish_key]['boss_name']} 大哥, 这里这里")

                    else:
                        if random()<0.3:
                            re_message1 = await app.send_message(message.chat.id,f"{lottery_list[finish_key]['boss_name']}大佬, \n我的是这个: {my_ptid}")
                        elif random()>0.7:
                            re_message1 = await app.send_message(message.chat.id,f"{lottery_list[finish_key]['boss_name']}哥, \n打这里 {my_ptid}")
                        else:
                            re_message1 = await app.send_message(message.chat.id,f"这位爷,我的用户名是: {my_ptid}")
    
                else:
                    if lottery_list.get(finish_key):
                        if lottery_list[finish_key]['flag'] == 1:
                            await asyncio.sleep(randint(20, 40)) 
                            if random() > 0.001:
                                logger.info(f"随机概率中标,发送未中奖黑幕")
                                if random() > 0.55:
                                    re_message1 = await app.send_message(message.chat.id,f"{heimu_REPLY_MESSAGE[randint(1,5)]}")
                                else:
                                    await app.send_sticker(message.chat.id, Sticker_REPLY_MESSAGE[f"heimu{randint(1,2)}"])
                            else:
                                logger.info(f"随机概率未中标,不发送未中奖黑幕")
            else:
                logger.info(f"抽奖是自己发起的，故不发黑幕,中奖也不领奖")


            if lottery_list.get(finish_key):
                del lottery_list[finish_key]
            logger.info(f"lottery_list aftter = {lottery_list} ") 

@app.on_message(custom_filters.reply_to_me
                & (filters.regex(r"机器人")
                | filters.regex(r"真人？")
                | filters.regex(r"脚本")
                | filters.regex(r"自动抽奖")
                | filters.regex(r"不是真人")
                | filters.regex(r"脚本抽奖")
                | filters.regex(r"机器人抽奖")
                | filters.regex(r"这个也是"))
                & filters.user                
                )
async def autolottery_negative_reply(client:Client, message:Message):
    await asyncio.sleep(randint(10,60))

    await message.reply(noautolottery_REPLY_MESSAGE[f"negative{randint(1,len(noautolottery_REPLY_MESSAGE))}"])



#################################中奖信息分析#########################
# 
# 
def parse_lottery_info(prize_info):
    # 使用正则表达式匹配奖品信息
    pattern = r'(?P<prize>.+?)\s*\*?\s*(?P<count>\d+)\s*：\s*(?P<winners>.+?)\n'
    matches = re.findall(pattern, prize_info, re.DOTALL)
    
    lottery_info = {}
    
    for match in matches:
        prize_name = match[0].strip()  # 奖品名称
        prize_count = int(match[1].strip())  # 奖品数量
        winners_info = match[2].strip().split('\n')  # 中奖者信息
        
        winners = []
        for winner_info in winners_info:
            # 使用正则表达式匹配中奖者的姓名和ID
            winner_pattern = r'▸\s*(?P<name>.+)\s+\((?P<id>\d+)\)\s+参与消息'
            winner_match = re.match(winner_pattern, winner_info)
            if winner_match:
                winner_data = {
                    'name': winner_match.group('name').strip(),
                    'id': winner_match.group('id').strip()
                }
                winners.append(winner_data)
        
        # 将奖品和中奖者信息存入字典
        lottery_info[prize_name] = {
            'prize_count': prize_count,
            'prize_winners': winners
        }
    
    return lottery_info

#################查找元素是否在字符串中存在，存咋则返回对应键####################### 
async def prize_check(prize_string):
    for key, prize_names in prize_list.items():
        for prize in prize_names:
            if prize in prize_string:
                return key
    return False
        
