import html
import json
import sys
import re

import requests as r
from bs4 import BeautifulSoup

from utils.exceptions import NoSuchWord
from utils.translate import translate
from modules.instance import logger


class Word:
    def __init__(self, word=None) -> None:
        self.result = {}
        if not word:
            self.url = f"https://www.dwds.de"
            response = r.get(self.url).text
            self.soup = BeautifulSoup(response, "html.parser")
            element = self.soup.select_one('a[href^="/wb/"]')
            href = element["href"]
            self.url += href
            self.word = href.split("/")[2]
            response = r.get(self.url).text
            self.soup = BeautifulSoup(response, "html.parser")
        else:
            self.word = word
            self.url = f"https://www.dwds.de/wb/{self.word}"
            response = r.get(self.url).text
            self.soup = BeautifulSoup(response, "html.parser")
        self.__check_existence()
        self.result["url"] = self.url
        self.result["url2"] = f"https://www.verben.de/?w={self.word}"
        logger.info(f"Try to parse word: {self.word}.")

    def __check_existence(self):
        """Check if a word exists by checking for a specific element on the page"""
        element_attrs = {"class": "col-md-12", "style": "margin-top:10px"}
        target_text = (
            f"Es tut uns leid, Ihre Anfrage {self.word} ist nicht "
            "in unseren gegenwartssprachlichen lexikalischen Quellen vorhanden."
        )
        element = self.soup.find("div", attrs=element_attrs)
        if element is not None and target_text in element.get_text():
            raise NoSuchWord(f"Unable to find the word ({self.word}).")

    def __decode_html_entities(self, text):
        """Decode HTML entities in the given text"""
        return html.unescape(text)

    def __remove_parentheses(self, text):
        """Remove parentheses from the given text"""
        return text.replace("(", "").replace(")", "")

    def __get_explanations(self):
        """Get explanations of the word"""
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
        """Get examples with the given word"""
        try:
            examples = self.soup.find_all("span", class_="dwdswb-belegtext")
            examples = [
                self.__decode_html_entities(example.text) for example in examples
            ]
            self.result["examples"] = examples
        except AttributeError:
            self.result["examples"] = None

    def __get_word_article(self, input_string) -> dict:
        data_list = input_string.split(", ")
        word = data_list[0]
        if len(data_list) > 1:
            components = data_list[1].split(" oder ")
        else:
            components = [None]
        result = {"word": self.__decode_html_entities(word.strip())}
        if len(components) > 1:
            articles = [
                self.__decode_html_entities(article.strip()) for article in components
            ]
            result["article"] = articles
        else:
            result["article"] = (
                self.__decode_html_entities(components[0].strip())
                if components[0]
                else None
            )
        return result

    def __get_grammar_data(self, input_string):
        data_dict = {
            "grammar": None,
            "word_type": None,
            "gender": None,
            "gen_singular": None,
            "plural": None,
        }
        gender = None
        # pattern = r"(.*?) \((.*?)\) \u00b7 Genitiv Singular: (.*?) \u00b7 Nominativ Plural: (.*)"
        pattern = r"(.*?) \((.*?)\)(?:, meist ohne Artikel)? \u00b7 Genitiv Singular: (.*?)(?: \u00b7 Nominativ Plural: (.*?))?(?: \u00b7 wird nur im Singular verwendet)?$"
        match_elements = re.match(
            pattern=pattern, string=input_string, flags=re.UNICODE
        )
        if match_elements:
            data_dict["word_type"] = (
                self.__decode_html_entities(match_elements.group(1).lower())
                if match_elements.group(1)
                else None
            )
            if match_elements.group(2):
                if len(match_elements.group(2).split(", ")) > 1:
                    gender = [
                        self.__decode_html_entities(g.lower())
                        for g in match_elements.group(2).split(", ")
                    ]
                else:
                    gender = self.__decode_html_entities(
                        match_elements.group(2).lower()
                    )
            else:
                gender = None
            data_dict["gender"] = gender
            data_dict["gen_singular"] = (
                self.__decode_html_entities(match_elements.group(3))
                if match_elements.group(3)
                else None
            )
            data_dict["plural"] = (
                self.__decode_html_entities(match_elements.group(4))
                if match_elements.group(4)
                else "wird nur im Singular verwendet"
            )
        data_dict["grammar"] = input_string.replace(" \u00b7 ", "\n")
        return data_dict

    def get_info(self):
        """Get detailed information about the word"""
        string = self.soup.find("h1", class_="dwdswb-ft-lemmaansatz").text
        self.result.update(self.__get_word_article(string))
        self.result["translations"] = translate(self.result["word"])
        self.result.update(
            self.__get_grammar_data(
                self.soup.find("span", class_="dwdswb-ft-blocktext").text
            )
        )
        try:
            self.result["ipa"] = self.__decode_html_entities(
                self.soup.find("span", class_="dwdswb-ipa").text
            )
        except AttributeError:
            self.result["ipa"] = None
        self.__get_explanations()
        self.__get_examples()
        gender_to_article = {
            "femininum": "die*",
            "maskulinum": "der*",
            "neutrum": "das*",
        }
        if self.result["article"] == "ohne Artikel" and self.result["gender"]:
            if isinstance(self.result["gender"], list):
                articles = []
                for gender in self.result["gender"]:
                    articles.append(gender_to_article[gender])
                self.result["article"] = articles
            else:
                self.result["article"] = gender_to_article[self.result["gender"]]
        return self.result


def main():
    if len(sys.argv) > 1:
        inp_word = sys.argv[1]
    else:
        inp_word = None
    w = Word(inp_word)
    try:
        result = w.get_info()
        with open(f"etc/{inp_word}.json", "w") as file:
            json.dump(result, file)
    except NoSuchWord:
        print("Word not found.")


if __name__ == "__main__":
    main()
