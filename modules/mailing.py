import random
from datetime import datetime
import os
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
    flags,
)
from modules.keyboards import get_back_menu, get_mailing_menu, WordCallback
from utils.word import Word
from utils.exceptions import NoSuchWord
from utils.escape import markdown_escape


async def generate_word_of_the_day():
    words.load_data()
    daily_words.load_data()

    w = Word()
    try:
        data = w.get_info()
    except NoSuchWord as e:
        logger.warning(f"({w.word}) {e}")

    today_date = datetime.now().strftime("%d.%m.%Y")

    if today_date in daily_words:
        logger.error("The mailing has already been sent out today.")
        logger.warning(
            f"'{daily_words[today_date]['word']}' already exist in database."
        )
        return None

    if data["word"] not in words:
        words[data["word"]] = data
        words[data["word"]].save()

    logger.info(f"Word of the day - {data['word']}.")
    daily_words[today_date] = data
    daily_words[today_date].save()
    return data


async def send_word_of_the_day(bot: Bot):
    messages.load_data()

    emojies = messages["emojies"]["list"]
    word = await generate_word_of_the_day()

    if not word:
        admin_message = markdown_escape(
            "⚠️ The mailing has already been sent out today."
        )
        await bot.send_message(
            chat_id=os.getenv("ADMIN"),
            text=admin_message,
        )
        return

    for user_id in subscribed_users:
        try:
            text = messages["word_of_the_day"]["text"].format(
                emoji=random.choice(emojies),
                article=markdown_escape(word.get("article", "")),
                word=markdown_escape(word.get("word", "")),
                explanation=markdown_escape(word.get("explanations", [""])[0]),
                example=markdown_escape(word.get("examples", [""])[0]),
            )
            reply_markup = get_mailing_menu(
                word.get("word", ""), sect_from="mailing_menu"
            )
            await bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
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
    article = markdown_escape(word.get("article", ""))
    grammar = markdown_escape(word.get("grammar", ""))
    ipa = (
        f"🗣 Aussprache: [_{markdown_escape(word['ipa'])}_]" if word.get("ipa") else "\r"
    )

    await bot.edit_message_text(
        text=messages["word_grammar"]["text"].format(
            article=article,
            word=markdown_escape(word.get("word", "")),
            grammar=grammar,
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
    word["article"] = markdown_escape(word.get("article", ""))
    # Create a formatted explanations string
    explanations = "\n".join(
        f"{messages['word_explanations']['emoji']} {markdown_escape(expl)}"
        for expl in word.get("explanations", [])[:20]
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
    word["article"] = markdown_escape(word.get("article", ""))
    # Create a formatted examples string
    examples = "\n".join(
        f"{messages['word_examples']['emoji']} {markdown_escape(exmpl)}"
        for exmpl in word.get("examples", [])[:20]
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
    word["article"] = markdown_escape(word.get("article", ""))
    translations = ""

    for country, translation in word.get("translations", {}).items():
        try:
            flag = flags.get(country.upper(), "🧐")
            translations += f"{flag}: {markdown_escape(translation)}\n"
        except KeyError:
            logger.warning(f"No Flag for country: {country}.")
            translations += f"🧐: {markdown_escape(translation)}\n"

    await bot.edit_message_text(
        text=messages["word_translation"]["text"].format(
            translations=translations, word=word
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
                article=markdown_escape(word.get("article", "")),
                word=markdown_escape(word.get("word", "")),
                explanation=markdown_escape(word.get("explanations", [""])[0]),
                example=markdown_escape(word.get("examples", [""])[0]),
            ),
            message_id=query.message.message_id,
        )
    elif callback_data.section_to == "start":
        word["article"] = markdown_escape(word.get("article", ""))
        word["explanations"] = [
            markdown_escape(expl) for expl in word.get("explanations", [])[:20]
        ]
        word["examples"] = [
            markdown_escape(examp) for examp in word.get("examples", [])[:20]
        ]

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
