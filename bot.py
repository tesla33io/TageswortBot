import asyncio
from datetime import datetime
import os

from aiogram import Dispatcher, Bot

from modules.instance import dp, bot
from modules.commands import dp
from modules.mailing import dp


async def main(dispatcher: Dispatcher, telegram_bot: Bot):
    await dispatcher.start_polling(telegram_bot)


if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")
        print(f"Folder logs created.")
    else:
        print(f"Folder logs already exists.")
    asyncio.run(main(dp, bot))
