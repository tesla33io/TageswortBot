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


def get_back_menu(sect_from: str, sect_to: str, word: str) -> InlineKeyboardMarkup:
    messages.load_data()
    inline_btns = messages["inline_btns"]
    back_menu_builder = InlineKeyboardBuilder()
    back_menu_builder.button(
        text=inline_btns["back"],
        callback_data=WordCallback(
            section_from=sect_from, section_to=sect_to, word=word
        ),
    )
    return back_menu_builder.as_markup()


def get_mailing_menu(word: str, sect_from: str) -> InlineKeyboardMarkup:
    messages.load_data()
    inline_btns = messages["inline_btns"]
    mailing_menu_builder = InlineKeyboardBuilder()
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["grammar"],
        callback_data=WordCallback(
            section_from=sect_from, section_to="grammar", word=word
        ),
    )
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["explanations"],
        callback_data=WordCallback(
            section_from=sect_from, section_to="explanations", word=word
        ),
    )
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["examples"],
        callback_data=WordCallback(
            section_from=sect_from, section_to="examples", word=word
        ),
    )
    mailing_menu_builder.button(
        text=inline_btns["mailing_menu"]["translations"],
        callback_data=WordCallback(
            section_from=sect_from, section_to="translations", word=word
        ),
    )
    mailing_menu_builder.adjust(3, repeat=True)
    return mailing_menu_builder.as_markup()
