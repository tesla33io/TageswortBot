from datetime import datetime
import random
import os

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode

from modules.instance import (
    logger,
    bot,
    dp,
    users,
    subscribed_users,
    messages,
    daily_words,
    words,
    user_document_template,
    subscriber_document_template,
)
from modules.keyboards import get_mailing_menu
from utils.translate import fix_translate
from utils.escape import markdown_escape


@dp.message(Command("start"))
async def on_start(message: Message):
    messages.load_data()
    daily_words.load_data()
    user_id = message.from_user.id
    if user_id in users and user_id in subscribed_users:
        try:
            word = daily_words[datetime.now().strftime("%d.%m.%Y")]
            word["article"] = markdown_escape(word["article"]) if word["article"] else ""
            word["explanations"] = [markdown_escape(expl) for expl in word["explanations"]]
            word["examples"] = [markdown_escape(examp) for examp in word["examples"]]
            await bot.send_message(
                chat_id=message.chat.id,
                text=messages["todays_word"]["text"].format(
                    emoji=random.choice(messages["emojies"]["list"]), word=word
                ),
                reply_markup=get_mailing_menu(word=word["word"], sect_from="start"),
            )
        except KeyError:
            await bot.send_message(
                chat_id=message.chat.id,
                text=messages["no_word_for_today"]["text"]
            )
    elif user_id in users and user_id not in subscribed_users:
        subscribed_users[user_id] = subscriber_document_template
        subscribed_users[user_id].save()
        await bot.send_message(
            chat_id=message.chat.id,
            text=messages["on_subscribe"]["text"],
        )
    else:
        user_document_template["date_joined"] = datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )
        users[user_id] = user_document_template
        users[user_id].save()
        subscribed_users[user_id] = subscriber_document_template
        subscribed_users[user_id].save()
        await bot.send_message(
            chat_id=message.chat.id,
            text=messages["welcome"]["text"].format(user=message.from_user),
        )


@dp.message(Command("abmelden"))
async def on_unsubscribe(message: Message):
    messages.load_data()
    user_id = message.from_user.id
    if user_id in subscribed_users:
        subscribed_users.delete(user_id)
        if user_id not in subscribed_users:
            await bot.send_message(
                chat_id=user_id,
                text=messages["unsubscribe_success"]["text"],
            )
            return
        else:
            logger.error(f"Failed unsubscription. User id: {user_id}")
            await bot.send_message(
                chat_id=user_id,
                text=messages["unsubscribe_fail"]["text"],
            )
            return
    await bot.send_message(
        chat_id=user_id,
        text=messages["unsubscribe_already"]["text"],
    )


@dp.message(Command("fix_translate"), F.chat.id == int(os.getenv("ADMIN")))
async def on_fix_translate(message: Message):
    # The source for translations contains some incorrect country
    # codes for translations in the corresponding language,
    # this function should fix it
    words.load_data()
    daily_words.load_data()
    i = 0
    corrected_words = []
    corrected_words.append("All words:")
    for word in words:
        logger.debug(word)
        new_translations = fix_translate(words[word]["translations"])
        if new_translations != words[word]["translations"]:
            i += 1
            corrected_words.append(word)
        words[word]["translations"] = new_translations
        words[word].save()
    corrected_words.append("\nDaily words:")
    for word in daily_words:
        logger.debug(word)
        new_translations = fix_translate(daily_words[word]["translations"])
        if new_translations != daily_words[word]["translations"]:
            i += 1
            corrected_words.append(word)
        daily_words[word]["translations"] = new_translations
        daily_words[word].save()
    await bot.send_message(
        chat_id=int(os.getenv("ADMIN")),
        text=markdown_escape(
            f"Corrected: {i} documents.\n" + ", ".join(w for w in corrected_words)
        )
    )
