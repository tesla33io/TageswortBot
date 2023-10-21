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
    user_id = message.from_user.id
    if user_id in users and user_id in subscribed_users:
        await bot.send_message(
            chat_id=message.chat.id,
            text=messages["welcome"]["text"].format(user=message.from_user),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif user_id in users and user_id not in subscribed_users:
        subscribed_users[user_id] = subscriber_document_template
        subscribed_users[user_id].save()
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Sie haben das Wort des Tages abonniert. Um sich abzumelden, schreiben Sie /unsubscribe",
            parse_mode=ParseMode.MARKDOWN,
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
            parse_mode=ParseMode.MARKDOWN,
        )


@dp.message(Command("unsubscribe"))
async def on_unsubscribe(message: Message):
    user_id = message.from_user.id
    if user_id in subscribed_users:
        subscribed_users.delete(user_id)
        if user_id not in subscribed_users:
            await bot.send_message(
                chat_id=user_id, text="Sie haben sich erfolgreich abgemeldet."
            )
            return
        else:
            logger.error(f"Failed unsubscription. User id: {user_id}")
            await bot.send_message(
                chat_id=user_id,
                text="Es ist ein Fehler aufgetreten. Sie haben sich nicht abgemeldet. Bitte kontaktieren Sie den Support.",
            )
            return
    await bot.send_message(chat_id=user_id, text="Sie haben sich bereits abgemeldet.")
