import asyncio
from random import randint, sample
from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from app.filters import custom_filters
from app import app
import logging

logger = logging.getLogger("main")

GROUP = -1002022762746
BOT = 7124396542


def card_value(card):
    if card[0] in "JQK":
        return 10
    elif card[0] == "A":
        return 1
    else:
        return int(card[0])


def calculate_score(cards):
    score = sum(card_value(card) for card in cards)
    if score <= 11 and any(card.startswith("A") for card in cards):
        score += 10
    return score


@app.on_message(
    filters.regex(
        r"庄：\?\?\? ((?:[2-9JQKA][♦♣♥♠]\s*)+)\n你(\d+)点：((?:[2-9JQKA][♦♣♥♠]\s*)+)"
    )
)
@app.on_edited_message(
    filters.regex(
        r"庄：\?\?\? ((?:[2-9JQKA][♦♣♥♠]\s*)+)\n你(\d+)点：((?:[2-9JQKA][♦♣♥♠]\s*)+)"
    )
)
async def blackjack(client: Client, message: Message):
    logger.info(message.text)
    match = message.matches[0]
    zhuang = match.group(1)
    ni_dianshu = match.group(2)
    ni = match.group(3)
    zhuang_cards = zhuang.split()
    ni_cards = ni.split()
    zhuang_score = calculate_score(zhuang_cards)
    ni_score = calculate_score(ni_cards)
    remaining_cards = [f"{rank}{suit}" for rank in "23456789JQKA" for suit in "♦♣♥♠"]
    for card in zhuang_cards + ni_cards:
        remaining_cards.remove(card)

    win_count = 0
    total_simulations = 10000

    for _ in range(total_simulations):
        zhuang_simulated = zhuang_cards[:]
        while calculate_score(zhuang_simulated) < 17:
            zhuang_simulated.append(sample(remaining_cards, 1)[0])

        zhuang_simulated_score = calculate_score(zhuang_simulated)

        if ni_score > zhuang_simulated_score or zhuang_simulated_score > 21:
            win_count += 1

    win_probability = win_count / total_simulations
    hit_win_count = 0
    for _ in range(total_simulations):
        ni_simulated = ni_cards[:]
        ni_simulated.append(sample(remaining_cards, 1)[0])
        ni_simulated_score = calculate_score(ni_simulated)
        if ni_simulated_score <= 21:
            zhuang_simulated = zhuang_cards[:]
            while calculate_score(zhuang_simulated) < 17:
                zhuang_simulated.append(sample(remaining_cards, 1)[0])

            zhuang_simulated_score = calculate_score(zhuang_simulated)

            if (
                ni_simulated_score > zhuang_simulated_score
                or zhuang_simulated_score > 21
            ):
                hit_win_count += 1

    hit_win_probability = hit_win_count / total_simulations
    await message.reply_text(
        f"庄的点数: {zhuang_score}\n你的点数: {ni_score}\n不拿获胜概率: {win_probability:.2%}\n拿牌获胜概率: {hit_win_probability:.2%}"
    )
