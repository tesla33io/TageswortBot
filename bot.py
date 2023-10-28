import asyncio

from aiogram import Dispatcher, Bot

from modules.instance import dp, bot
from modules.commands import dp
from modules.mailing import dp


async def main(dispatcher: Dispatcher, telegram_bot: Bot):
    await dispatcher.start_polling(telegram_bot)


if __name__ == "__main__":
    asyncio.run(main(dp, bot))
