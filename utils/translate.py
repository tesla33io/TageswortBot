import html
import json
import sys

import requests as r
from bs4 import BeautifulSoup


def translate(word: str) -> dict:
    url = f"https://www.verben.de/?w={word}"
    response = r.get(url).text
    result = {}
    soup = BeautifulSoup(response, "html.parser")
    translations = soup.find_all("dd", lang=True)
    for tr in translations:
        result[tr.get("lang")] = tr.text.replace("\u00a0", "")
    return result
