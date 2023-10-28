import html
import json
import sys

import requests as r
from bs4 import BeautifulSoup


def translate(word: str) -> dict:
    flag_change = {"ar": "arabic", "bl": "by"}
    url = f"https://www.verben.de/?w={word}"
    response = r.get(url).text
    result = {}
    soup = BeautifulSoup(response, "html.parser")
    translations = soup.find_all("dd", lang=True)
    for tr in translations:
        result[tr.get("lang")] = tr.text.replace("\u00a0", "")
    result = fix_translate(result)
    return result


def fix_translate(translations: dict) -> dict:
    # The source for translations contains some incorrect country
    # codes for translations in the corresponding language,
    # this function should fix it
    flag_change = {
        "ar": "sa",
        "bl": "by",
        "da": "dk",
        "cs": "cz",
        "en": "gb",
        "uk": "ua",
        "el": "gr",
        "sv": "se",
    }
    new_translations = translations.copy()
    for tr, new_key in flag_change.items():
        if tr in new_translations:
            new_translations[new_key] = new_translations.pop(tr)
    return new_translations
