import asyncio
from datetime import datetime
import os

from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.instance import dp, bot, logger, subscribed_users, scheduler
from modules.commands import dp
from modules.mailing import send_word_of_the_day


async def main(dispatcher: Dispatcher, telegram_bot: Bot):
    scheduler.add_job(
        send_word_of_the_day, "cron", hour=int(datetime.now().strftime('%H')), minute=int(datetime.now().strftime('%M')) + 1, second=0, args=[bot]
    )
    scheduler.start()
    await dispatcher.start_polling(telegram_bot)


if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")
        print(f"Folder logs created.")
    else:
        print(f"Folder logs already exists.")
    asyncio.run(main(dp, bot))
