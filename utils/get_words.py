import requests as r


def get_words(number: int) -> list:
    url = f"https://alex-riedel.de/randV2.php?anz={number}"
    response = r.get(url).json()
    return response
