import random
from datetime import datetime
import os

from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode

from modules.instance import logger, subscribed_users, daily_words, words, messages
from utils.word import Word
from utils.get_words import get_words
from utils.exceptions import NoSuchWord

emojies = "👉🤓🙊🌞🔥🚨💡📻🔮🪄📫📆💬"


async def generate_word_of_the_day():
    try:
        w = Word()
    except NoSuchWord:
        w = Word()
    data = w.get_info()
    if datetime.now().strftime("%d.%m.%Y") in daily_words:
        logger.error("The mailing has already been sent out today.")
        logger.warn(
            f"'{words[datetime.now().strftime('%d.%m.%Y')]['word']}' already exist in database."
        )
        return None
    if data["word"] not in words:
        words[data['word']] = data
        words[data['word']].save()
    daily_words[datetime.now().strftime("%d.%m.%Y")] = data
    daily_words[datetime.now().strftime("%d.%m.%Y")].save()
    return data


async def send_word_of_the_day(bot: Bot):
    word = await generate_word_of_the_day()
    if not word:
        await bot.send_message(
            chat_id=os.getenv("ADMIN"),
            text="⚠️ The mailing has already been sent out today.",
        )
        return
    for user_id in subscribed_users:
        await bot.send_message(
            chat_id=user_id,
            text=messages["word_of_the_day"]["text"].format(
                emoji=random.choice(emojies),
                article=word["article"],
                word=word["word"],
                explanations=word["explanations"],
                examples=word["examples"],
            ),
            parse_mode=ParseMode.MARKDOWN
        )
