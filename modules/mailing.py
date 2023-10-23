import random
from datetime import datetime
import os
import re

from aiogram import Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode

from modules.instance import logger, subscribed_users, daily_words, words, messages, dp, bot
from modules.keyboards import get_back_menu, get_mailing_menu, MailingCallback
from utils.word import Word
from utils.get_words import get_words
from utils.exceptions import NoSuchWord


async def generate_word_of_the_day():
    success = False
    while not success:
        w = Word()
        try:
            data = w.get_info()
            success = True
        except NoSuchWord as e:
            logger.warn(f"({w.original}) {e}")
    if datetime.now().strftime("%d.%m.%Y") in daily_words:
        logger.error("The mailing has already been sent out today.")
        logger.warn(
            f"'{daily_words[datetime.now().strftime('%d.%m.%Y')]['word']}' already exist in database."
        )
        return None
    if data["word"] not in words:
        words[data["word"]] = data
        words[data["word"]].save()
    logger.info(f"Word of the day - {data['word']}.")
    daily_words[datetime.now().strftime("%d.%m.%Y")] = data
    daily_words[datetime.now().strftime("%d.%m.%Y")].save()
    return data


async def send_word_of_the_day(bot: Bot):
    messages.load_data()
    emojies = messages["emojies"]["list"]
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
                explanation=re.escape(word["explanations"][0]),
                example=re.escape(word["examples"][0]),
            ),
            reply_markup=get_mailing_menu(word=word["word"], sect_from="mailing_menu"),
        )


@dp.callback_query(MailingCallback.filter(F.section_to == "grammar"))
async def send_mailing_grammar(
    query: CallbackQuery, callback_data: MailingCallback, bot: Bot
):
    messages.load_data()
    word = words[callback_data.word]
    gender_emojies = {"neutrum": "🟢", "maskulinum": "🔵", "femininum": "🟣"}
    gender_emoji = gender_emojies[word["gender"]]
    ipa = f"🗣 Aussprache: [_{re.escape(word['ipa'])}_]" if word["ipa"] else "\r"
    await bot.edit_message_text(
        text=messages["word_grammar"]["text"].format(
            article=word["article"],
            word=word["word"],
            gender_emoji=gender_emoji,
            gender=word["gender"],
            plural=word["plural"],
            word_type=word["word_type"],
            gen_singular=re.escape(word["gen_singular"]),
            ipa=ipa,
        ),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=get_back_menu(
            sect_from="grammar", sect_to="mailing_menu", word=word["word"]
        ),
    )


@dp.callback_query(MailingCallback.filter(F.section_to == "mailing_menu"))
async def return_to_main_mailing_message(
    query: CallbackQuery, callback_data: MailingCallback, bot: Bot
):
    user_id = query.from_user.id
    messages.load_data()
    emojies = messages["emojies"]["list"]
    word = words[callback_data.word]
    await bot.edit_message_text(
        chat_id=user_id,
        text=messages["word_of_the_day"]["text"].format(
            emoji=random.choice(emojies),
            article=word["article"],
            word=word["word"],
            explanation=re.escape(word["explanations"][0]),
            example=re.escape(word["examples"][0]),
        ),
        message_id=query.message.message_id,
    )
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=query.message.message_id,
        reply_markup=get_mailing_menu(word=word["word"], sect_from="mailing_menu"),
    )


if __name__ == "__main__":
    send_word_of_the_day(bot=bot)