from datetime import datetime

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
    user_document_template,
    subscriber_document_template,
)


@dp.message(Command("start"))
async def on_start(message: Message):
    messages.load_data()
    user_id = message.from_user.id
    if user_id in users and user_id in subscribed_users:
        await bot.send_message(
            chat_id=message.chat.id,
            text=messages["welcome"]["text"].format(user=message.from_user),
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
