import logging
from datetime import datetime
import os

from aiogram import Dispatcher, Bot
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.database_manager import MongoDBCollection


load_dotenv()
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename=f"logs/tageswort_{datetime.now().strftime('%d.%m.%Y')}.log",
    encoding="utf-8",
    level=logging.INFO,
    format="[%(levelname)s] (%(asctime)s) %(name)s : %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Europe/Berlin")
bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher()
users = MongoDBCollection("user_management", "users", os.getenv("DB_URI"))
subscribed_users = MongoDBCollection(
    "user_management", "subscribed_users", os.getenv("DB_URI")
)
daily_words = MongoDBCollection("information", "daily_words", os.getenv("DB_URI"))
words = MongoDBCollection("information", "words", os.getenv("DB_URI"))
messages = MongoDBCollection("information", "messages", os.getenv("DB_URI"))
user_document_template = {"date_joined": None, "score": 0, "is_admin": False}
subscriber_document_template = {"subscribed": True}
