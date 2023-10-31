from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from modules.instance import messages


class WordCallback(CallbackData, prefix="word"):
    section_from: str
    section_to: str
    word: str


def create_word_callback(section_from, section_to, word):
    return WordCallback(section_from=section_from, section_to=section_to, word=word)


def get_back_menu(sect_from: str, sect_to: str, word: str) -> InlineKeyboardMarkup:
    messages.load_data()
    inline_btns = messages["inline_btns"]
    back_menu_builder = InlineKeyboardBuilder()
    back_menu_builder.button(
        text=inline_btns["back"],
        callback_data=create_word_callback(sect_from, sect_to, word),
    )
    return back_menu_builder.as_markup()


def get_mailing_menu(word: str, sect_from: str) -> InlineKeyboardMarkup:
    messages.load_data()
    inline_btns = messages["inline_btns"]
    mailing_menu_builder = InlineKeyboardBuilder()
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["grammar"],
        callback_data=create_word_callback(sect_from, "grammar", word),
    )
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["explanations"],
        callback_data=create_word_callback(sect_from, "explanations", word),
    )
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["examples"],
        callback_data=create_word_callback(sect_from, "examples", word),
    )
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["translations"],
        callback_data=create_word_callback(sect_from, "translations", word),
    )
    mailing_menu_builder.adjust(3, repeat=True)
    return mailing_menu_builder.as_markup()
