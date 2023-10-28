import random
from datetime import datetime
import os
import re
import asyncio

from aiogram import Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from modules.instance import (
    logger,
    subscribed_users,
    daily_words,
    words,
    messages,
    dp,
    bot,
    flags
)
from modules.keyboards import get_back_menu, get_mailing_menu, WordCallback
from utils.word import Word
from utils.exceptions import NoSuchWord


async def generate_word_of_the_day():
    success = False
    while not success:
        w = Word()
        try:
            data = w.get_info()
            success = True
        except NoSuchWord as e:
            logger.warning(f"({w.original}) {e}")
    if datetime.now().strftime("%d.%m.%Y") in daily_words:
        logger.error("The mailing has already been sent out today.")
        logger.warning(
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
            text="⚠️ The mailing has already been sent out today\.",
        )
        return
    for user_id in subscribed_users:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=messages["word_of_the_day"]["text"].format(
                    emoji=random.choice(emojies),
                    article=re.escape(word["article"]),
                    word=re.escape(word["word"]),
                    explanation=re.escape(word["explanations"][0]),
                    example=re.escape(word["examples"][0]),
                ),
                reply_markup=get_mailing_menu(word=word["word"], sect_from="mailing_menu"),
            )
        except TelegramBadRequest:
            logger.warning(f"Cannot send a message to the user {user_id}.")


@dp.callback_query(WordCallback.filter(F.section_to == "grammar"))
async def send_word_grammar(
    query: CallbackQuery, callback_data: WordCallback, bot: Bot
):
    messages.load_data()
    words.load_data()
    word = words[callback_data.word]
    gender_emojies = {"neutrum": "🟢", "maskulinum": "🔵", "femininum": "🟣"}
    if isinstance(word["gender"], list):
        gender = ""
        gender_emoji = ""
        for gender in word["gender"]:
            gender += re.escape(f"({gender_emojies[gender]} {gender}) ")
    else:
        try:
            gender_emoji = gender_emojies[word["gender"]]
        except KeyError:
            gender_emoji = "⚪️"
        gender = re.escape(word["gender"])
    ipa = f"🗣 Aussprache: [_{re.escape(word['ipa'])}_]" if word["ipa"] else "\r"
    await bot.edit_message_text(
        text=messages["word_grammar"]["text"].format(
            article=re.escape(word["article"]),
            word=re.escape(word["word"]),
            gender_emoji=gender_emoji,
            gender=gender,
            plural=re.escape(word["plural"]),
            word_type=re.escape(word["word_type"]),
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
            sect_from=callback_data.section_to,
            sect_to=callback_data.section_from,
            word=callback_data.word,
        ),
    )


@dp.callback_query(WordCallback.filter(F.section_to == "explanations"))
async def send_word_explanations(
    query: CallbackQuery, callback_data: WordCallback, bot: Bot
):
    messages.load_data()
    words.load_data()
    word = words[callback_data.word]
    word["article"] = re.escape(word["article"])
    word["explanations"] = [expl.replace("=", "") for expl in word["explanations"]]
    explanations = "\n".join(
        f"{messages['word_explanations']['emoji']} {re.escape(expl)}"
        for expl in word["explanations"]
    )
    await bot.edit_message_text(
        text=messages["word_explanations"]["text"].format(
            explanations=explanations, word=word
        ),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=get_back_menu(
            sect_from=callback_data.section_to,
            sect_to=callback_data.section_from,
            word=callback_data.word,
        ),
    )


@dp.callback_query(WordCallback.filter(F.section_to == "examples"))
async def send_word_examples(
    query: CallbackQuery, callback_data: WordCallback, bot: Bot
):
    messages.load_data()
    words.load_data()
    word = words[callback_data.word]
    word["article"] = re.escape(word["article"])
    word["examples"] = [examp.replace("=", "") for examp in word["examples"]]
    examples = "\n".join(
        f"{messages['word_examples']['emoji']} {re.escape(exmpl)}"
        for exmpl in word["examples"]
    )
    await bot.edit_message_text(
        text=messages["word_examples"]["text"].format(examples=examples, word=word),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=get_back_menu(
            sect_from=callback_data.section_to,
            sect_to=callback_data.section_from,
            word=callback_data.word,
        ),
    )

@dp.callback_query(WordCallback.filter(F.section_to == "translations"))
async def send_word_translations(
    query: CallbackQuery, callback_data: WordCallback, bot: Bot
):
    messages.load_data()
    words.load_data()
    word = words[callback_data.word]
    word["article"] = re.escape(word["article"])
    translations = ""
    for country in word["translations"]:
        translation = word["translations"][country]
        try:
            translations += f"{flags[country.upper()]}: {re.escape(translation)}\n"
        except KeyError:
            logger.warning(f"No Flag for country: {country}.")
            translations += f"🧐: {re.escape(translation)}\n"
    await bot.edit_message_text(
        text=messages["word_translation"]["text"].format(translations=translations, word=word),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=get_back_menu(
            sect_from=callback_data.section_to,
            sect_to=callback_data.section_from,
            word=callback_data.word,
        ),
    )


@dp.callback_query(WordCallback.filter(F.section_to.in_({"mailing_menu", "start"})))
async def return_to_main_mailing_message(
    query: CallbackQuery, callback_data: WordCallback, bot: Bot
):
    user_id = query.from_user.id
    words.load_data()
    messages.load_data()
    emojies = messages["emojies"]["list"]
    word = words[callback_data.word]
    if callback_data.section_to == "mailing_menu":
        await bot.edit_message_text(
            chat_id=user_id,
            text=messages["word_of_the_day"]["text"].format(
                emoji=random.choice(emojies),
                article=re.escape(word["article"]),
                word=re.escape(word["word"]),
                explanation=re.escape(word["explanations"][0]),
                example=re.escape(word["examples"][0]),
            ),
            message_id=query.message.message_id,
        )
    elif callback_data.section_to == "start":
        word["article"] = re.escape(word["article"])
        word["explanations"] = [re.escape(expl) for expl in word["explanations"]]
        word["examples"] = [re.escape(examp) for examp in word["examples"]]
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=messages["todays_word"]["text"].format(
                emoji=random.choice(emojies), word=word
            ),
        )
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=query.message.message_id,
        reply_markup=get_mailing_menu(
            word=callback_data.word, sect_from=callback_data.section_to
        ),
    )


if __name__ == "__main__":
    asyncio.run(send_word_of_the_day(bot=bot))
