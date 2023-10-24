from datetime import datetime
import random
import re

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
    user_document_template,
    subscriber_document_template,
)
from modules.keyboards import get_mailing_menu


@dp.message(Command("start"))
async def on_start(message: Message):
    messages.load_data()
    daily_words.load_data()
    user_id = message.from_user.id
    if user_id in users and user_id in subscribed_users:
        word = daily_words[datetime.now().strftime("%d.%m.%Y")]
        word["explanations"] = [re.escape(expl) for expl in word["explanations"]]
        word["examples"] = [re.escape(examp) for examp in word["examples"]]
        await bot.send_message(
            chat_id=message.chat.id,
            text=messages["todays_word"]["text"].format(
                emoji=random.choice(messages["emojies"]["list"]), word=word
            ),
            reply_markup=get_mailing_menu(word=word["word"], sect_from="start"),
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
