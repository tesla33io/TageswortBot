import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.instance import dp, bot, scheduler
from modules.commands import dp
from modules.mailing import send_word_of_the_day


async def main(dispatcher: Dispatcher, telegram_bot: Bot):
    await dispatcher.start_polling(telegram_bot)


if __name__ == "__main__":
    asyncio.run(main(dp, bot))
