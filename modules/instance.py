import logging
from datetime import datetime
import os
import sys

from aiogram import Dispatcher, Bot
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.database_manager import MongoDBCollection


load_dotenv()
if not os.path.exists("logs"):
    os.makedirs("logs")

# LOGGING
formatter = logging.Formatter("[%(levelname)s] (%(asctime)s) %(name)s : %(message)s", datefmt="%d.%m.%Y %H:%M:%S")

# logger_stdout_handler = logging.StreamHandler(sys.stdout)
# logger_stdout_handler.setLevel(logging.INFO)
# logger_stdout_handler.setFormatter(formatter)

# logger_file_handler = logging.FileHandler(f"logs/tageswort_{datetime.now().strftime('%d.%m.%Y')}.log")
# logger_file_handler.setLevel(logging.DEBUG)
# logger_file_handler.setFormatter(formatter)

# logger = logging.getLogger(__name__)
# logger.root.setLevel(logging.NOTSET)
# logger.addHandler(logger_stdout_handler)
# logger.addHandler(logger_file_handler)
logging.basicConfig(
    # filename=f"logs/tageswort_{datetime.now().strftime('%d.%m.%Y')}.log",
    encoding="utf-8",
    level=logging.NOTSET,
    format="[%(levelname)s] (%(asctime)s) %(name)s : %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

logger_stdout_handler = logging.StreamHandler(sys.stdout)
logger_stdout_handler.setLevel(logging.INFO)
logger_stdout_handler.setFormatter(formatter)

logger_file_handler = logging.FileHandler(f"logs/tageswort_{datetime.now().strftime('%d.%m.%Y')}.log")
logger_file_handler.setLevel(logging.DEBUG)
logger_file_handler.setFormatter(formatter)

aiogram_logger = logging.getLogger('aiogram')
aiogram_logger.setLevel(logging.INFO)

logger.addHandler(logger_stdout_handler)
logger.addHandler(logger_file_handler)
aiogram_logger.addHandler(logger_file_handler)

# AIOGRAM
bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher()

# DATABASES
users = MongoDBCollection("user_management", "users", os.getenv("DB_URI"))
subscribed_users = MongoDBCollection(
    "user_management", "subscribed_users", os.getenv("DB_URI")
)
daily_words = MongoDBCollection("information", "daily_words", os.getenv("DB_URI"))
words = MongoDBCollection("information", "words", os.getenv("DB_URI"))
messages = MongoDBCollection("information", "messages", os.getenv("DB_URI"))

# CONSTANTS
user_document_template = {"date_joined": None, "score": 0, "is_admin": False}
subscriber_document_template = {"subscribed": True}
flags = {
    "AD": "🇦🇩",
    "AE": "🇦🇪",
    "AF": "🇦🇫",
    "AG": "🇦🇬",
    "AI": "🇦🇮",
    "AL": "🇦🇱",
    "AM": "🇦🇲",
    "AO": "🇦🇴",
    "AQ": "🇦🇶",
    "AR": "🇦🇷",
    "AS": "🇦🇸",
    "AT": "🇦🇹",
    "AU": "🇦🇺",
    "AW": "🇦🇼",
    "AX": "🇦🇽",
    "AZ": "🇦🇿",
    "BA": "🇧🇦",
    "BB": "🇧🇧",
    "BD": "🇧🇩",
    "BE": "🇧🇪",
    "BF": "🇧🇫",
    "BG": "🇧🇬",
    "BH": "🇧🇭",
    "BI": "🇧🇮",
    "BJ": "🇧🇯",
    "BL": "🇧🇱",
    "BM": "🇧🇲",
    "BN": "🇧🇳",
    "BO": "🇧🇴",
    "BQ": "🇧🇶",
    "BR": "🇧🇷",
    "BS": "🇧🇸",
    "BT": "🇧🇹",
    "BV": "🇧🇻",
    "BW": "🇧🇼",
    "BY": "🇧🇾",
    "BZ": "🇧🇿",
    "CA": "🇨🇦",
    "CC": "🇨🇨",
    "CD": "🇨🇩",
    "CF": "🇨🇫",
    "CG": "🇨🇬",
    "CH": "🇨🇭",
    "CI": "🇨🇮",
    "CK": "🇨🇰",
    "CL": "🇨🇱",
    "CM": "🇨🇲",
    "CN": "🇨🇳",
    "CO": "🇨🇴",
    "CR": "🇨🇷",
    "CU": "🇨🇺",
    "CV": "🇨🇻",
    "CW": "🇨🇼",
    "CX": "🇨🇽",
    "CY": "🇨🇾",
    "CZ": "🇨🇿",
    "DE": "🇩🇪",
    "DJ": "🇩🇯",
    "DK": "🇩🇰",
    "DM": "🇩🇲",
    "DO": "🇩🇴",
    "DZ": "🇩🇿",
    "EC": "🇪🇨",
    "EE": "🇪🇪",
    "EG": "🇪🇬",
    "EH": "🇪🇭",
    "ER": "🇪🇷",
    "ES": "🇪🇸",
    "ET": "🇪🇹",
    "FI": "🇫🇮",
    "FJ": "🇫🇯",
    "FK": "🇫🇰",
    "FM": "🇫🇲",
    "FO": "🇫🇴",
    "FR": "🇫🇷",
    "GA": "🇬🇦",
    "GB": "🇬🇧",
    "GD": "🇬🇩",
    "GE": "🇬🇪",
    "GF": "🇬🇫",
    "GG": "🇬🇬",
    "GH": "🇬🇭",
    "GI": "🇬🇮",
    "GL": "🇬🇱",
    "GM": "🇬🇲",
    "GN": "🇬🇳",
    "GP": "🇬🇵",
    "GQ": "🇬🇶",
    "GR": "🇬🇷",
    "GS": "🇬🇸",
    "GT": "🇬🇹",
    "GU": "🇬🇺",
    "GW": "🇬🇼",
    "GY": "🇬🇾",
    "HK": "🇭🇰",
    "HM": "🇭🇲",
    "HN": "🇭🇳",
    "HR": "🇭🇷",
    "HT": "🇭🇹",
    "HU": "🇭🇺",
    "ID": "🇮🇩",
    "IE": "🇮🇪",
    "IL": "🇮🇱",
    "IM": "🇮🇲",
    "IN": "🇮🇳",
    "IO": "🇮🇴",
    "IQ": "🇮🇶",
    "IR": "🇮🇷",
    "IS": "🇮🇸",
    "IT": "🇮🇹",
    "JE": "🇯🇪",
    "JM": "🇯🇲",
    "JO": "🇯🇴",
    "JP": "🇯🇵",
    "KE": "🇰🇪",
    "KG": "🇰🇬",
    "KH": "🇰🇭",
    "KI": "🇰🇮",
    "KM": "🇰🇲",
    "KN": "🇰🇳",
    "KP": "🇰🇵",
    "KR": "🇰🇷",
    "KW": "🇰🇼",
    "KY": "🇰🇾",
    "KZ": "🇰🇿",
    "LA": "🇱🇦",
    "LB": "🇱🇧",
    "LC": "🇱🇨",
    "LI": "🇱🇮",
    "LK": "🇱🇰",
    "LR": "🇱🇷",
    "LS": "🇱🇸",
    "LT": "🇱🇹",
    "LU": "🇱🇺",
    "LV": "🇱🇻",
    "LY": "🇱🇾",
    "MA": "🇲🇦",
    "MC": "🇲🇨",
    "MD": "🇲🇩",
    "ME": "🇲🇪",
    "MF": "🇲🇫",
    "MG": "🇲🇬",
    "MH": "🇲🇭",
    "MK": "🇲🇰",
    "ML": "🇲🇱",
    "MM": "🇲🇲",
    "MN": "🇲🇳",
    "MO": "🇲🇴",
    "MP": "🇲🇵",
    "MQ": "🇲🇶",
    "MR": "🇲🇷",
    "MS": "🇲🇸",
    "MT": "🇲🇹",
    "MU": "🇲🇺",
    "MV": "🇲🇻",
    "MW": "🇲🇼",
    "MX": "🇲🇽",
    "MY": "🇲🇾",
    "MZ": "🇲🇿",
    "NA": "🇳🇦",
    "NC": "🇳🇨",
    "NE": "🇳🇪",
    "NF": "🇳🇫",
    "NG": "🇳🇬",
    "NI": "🇳🇮",
    "NL": "🇳🇱",
    "NO": "🇳🇴",
    "NP": "🇳🇵",
    "NR": "🇳🇷",
    "NU": "🇳🇺",
    "NZ": "🇳🇿",
    "OM": "🇴🇲",
    "PA": "🇵🇦",
    "PE": "🇵🇪",
    "PF": "🇵🇫",
    "PG": "🇵🇬",
    "PH": "🇵🇭",
    "PK": "🇵🇰",
    "PL": "🇵🇱",
    "PM": "🇵🇲",
    "PN": "🇵🇳",
    "PR": "🇵🇷",
    "PS": "🇵🇸",
    "PT": "🇵🇹",
    "PW": "🇵🇼",
    "PY": "🇵🇾",
    "QA": "🇶🇦",
    "RE": "🇷🇪",
    "RO": "🇷🇴",
    "RS": "🇷🇸",
    "RU": "🏴",
    "RW": "🇷🇼",
    "SA": "🇸🇦",
    "SB": "🇸🇧",
    "SC": "🇸🇨",
    "SD": "🇸🇩",
    "SE": "🇸🇪",
    "SG": "🇸🇬",
    "SH": "🇸🇭",
    "SI": "🇸🇮",
    "SJ": "🇸🇯",
    "SK": "🇸🇰",
    "SL": "🇸🇱",
    "SM": "🇸🇲",
    "SN": "🇸🇳",
    "SO": "🇸🇴",
    "SR": "🇸🇷",
    "SS": "🇸🇸",
    "ST": "🇸🇹",
    "SV": "🇸🇻",
    "SX": "🇸🇽",
    "SY": "🇸🇾",
    "SZ": "🇸🇿",
    "TC": "🇹🇨",
    "TD": "🇹🇩",
    "TF": "🇹🇫",
    "TG": "🇹🇬",
    "TH": "🇹🇭",
    "TJ": "🇹🇯",
    "TK": "🇹🇰",
    "TL": "🇹🇱",
    "TM": "🇹🇲",
    "TN": "🇹🇳",
    "TO": "🇹🇴",
    "TR": "🇹🇷",
    "TT": "🇹🇹",
    "TV": "🇹🇻",
    "TW": "🇹🇼",
    "TZ": "🇹🇿",
    "UA": "🇺🇦",
    "UG": "🇺🇬",
    "UM": "🇺🇲",
    "US": "🇺🇸",
    "UY": "🇺🇾",
    "UZ": "🇺🇿",
    "VA": "🇻🇦",
    "VC": "🇻🇨",
    "VE": "🇻🇪",
    "VG": "🇻🇬",
    "VI": "🇻🇮",
    "VN": "🇻🇳",
    "VU": "🇻🇺",
    "WF": "🇼🇫",
    "WS": "🇼🇸",
    "YE": "🇾🇪",
    "YT": "🇾🇹",
    "ZA": "🇿🇦",
    "ZM": "🇿🇲",
    "ZW": "🇿🇼",

    "ARABIC": "🇸🇦"
}
