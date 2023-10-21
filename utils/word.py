import html
import json
import sys

import requests as r
from bs4 import BeautifulSoup

from utils.exceptions import NoSuchWord
from utils.get_words import get_words
from utils.translate import translate


class Word:
    def __init__(self, word=None) -> None:
        if not word:
            word = get_words(1)[0]
        self.original = word
        self.url = f"https://www.dwds.de/?q={self.original}&from=wb"
        response = r.get(self.url).text
        self.result = {}
        self.soup = BeautifulSoup(response, "html.parser")

    def __decode_html_entities(self, text):
        # Decode HTML entities in the given text
        return html.unescape(text)

    def __remove_parentheses(self, text):
        # Remove parentheses from the given text
        return text.replace("(", "").replace(")", "")

    def __get_explanations(self):
        # Get explanations of the word
        try:
            explanations = self.soup.find_all("span", class_="dwdswb-definition")
            explanations = [
                self.__decode_html_entities(explanation.text)
                for explanation in explanations
            ]
            self.result["explanations"] = explanations
        except AttributeError:
            self.result["explanations"] = None

    def __get_examples(self):
        # Get examples with the given word
        try:
            examples = self.soup.find_all("span", class_="dwdswb-belegtext")
            examples = [
                self.__decode_html_entities(example.text) for example in examples
            ]
            self.result["examples"] = examples
        except AttributeError:
            self.result["examples"] = None

    def get_info(self):
        # Get detailed information about the word
        self.result["original"] = self.original
        try:
            word, article = self.__decode_html_entities(
                self.soup.find("h1", class_="dwdswb-ft-lemmaansatz").text
            ).split(", ")
            if not word == self.original:
                raise NoSuchWord("The original word does not match the found one.")
            self.result["word"] = word
            self.result["article"] = article
            self.result["translations"] = translate(word)
        except AttributeError:
            self.result["word"] = None
            self.result["article"] = None
        try:
            type_and_gender, genetive_singular, plural = self.soup.find(
                "span", class_="dwdswb-ft-blocktext"
            ).text.split(" \u00b7 ")
            word_type = self.__decode_html_entities(
                type_and_gender.split(" ")[0].lower()
            )
            gender = self.__decode_html_entities(
                self.__remove_parentheses(type_and_gender.split(" ")[1].lower())
            )
            genetive_singular = self.__decode_html_entities(
                genetive_singular.split(": ")[1]
            )
            plural = self.__decode_html_entities(plural.split(": ")[1])
            self.result["gender"] = gender
            self.result["gen_singular"] = genetive_singular
            self.result["word_type"] = word_type
            self.result["plural"] = plural
        except AttributeError:
            self.result["gender"] = None
            self.result["gen_singular"] = None
            self.result["word_type"] = None
            self.result["plural"] = None
        try:
            self.result["ipa"] = self.__decode_html_entities(
                self.soup.find("span", class_="dwdswb-ipa").text
            )
        except AttributeError:
            self.result["ipa"] = None
        self.__get_explanations()
        self.__get_examples()
        return self.result


def main():
    if len(sys.argv) > 1:
        inp_word = sys.argv[1]
    else:
        inp_word = get_words(1)[0]
    w = Word(inp_word)
    try:
        result = w.get_info()
        with open(f"etc/{inp_word}.json", "w") as file:
            json.dump(result, file)
    except NoSuchWord:
        print("Word not found.")


if __name__ == "__main__":
    main()
