import html
import json
import sys
import re

import requests as r
from bs4 import BeautifulSoup

from utils.exceptions import NoSuchWord
from utils.translate import translate


class Word:
    def __init__(self, word=None) -> None:
        if not word:
            self.url = f"https://www.dwds.de"
            response = r.get(self.url).text
            self.result = {}
            self.soup = BeautifulSoup(response, "html.parser")
            element = self.soup.select_one('a[href^="/wb/"]')
            href = element["href"]
            self.url += href
            self.word = href.split("/")[2]
            response = r.get(self.url).text
            self.soup = BeautifulSoup(response, "html.parser")
            print(self.soup.title)
        else:
            self.word = word
            self.url = f"https://www.dwds.de/wb/{word}"
            response = r.get(self.url).text
            self.result = {}
            self.soup = BeautifulSoup(response, "html.parser")
            print(self.soup.title)
        self.__check_existence()

    def __check_existence(self):
        """Check if a word exists by checking for a specific element on the page"""
        element_attrs = {"class": "col-md-12", "style": "margin-top:10px"}
        target_text = (
            f"Es tut uns leid, Ihre Anfrage {self.word} ist nicht "
            "in unseren gegenwartssprachlichen lexikalischen Quellen vorhanden."
        )
        # Find the <div> element with the specified attributes
        element = self.soup.find("div", attrs=element_attrs)
        # Check if the element is found and contains the target text
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

    def __find_element(self, source, default=None):
        try:
            return source
        except AttributeError:
            return default

    def __get_word_article(self, input_string) -> dict:
        # Split the input string by " oder " to handle both cases
        word = input_string.split(", ")[0]
        components = input_string.split(", ")[1].split(" oder ")
        # Create the JSON format object
        result = {"word": self.__decode_html_entities(word.strip())}
        # If there's more than one component, it means there's more than one article
        if len(components) > 1:
            articles = [
                self.__decode_html_entities(article.strip()) for article in components
            ]
            result["article"] = articles
        else:
            result["article"] = self.__decode_html_entities(components[0].strip())
        return result

    def __get_grammar_data(self, input_string):
        # Initialize the dictionary with default values as None
        data_dict = {
            "word_type": None,
            "gender": None,
            "gen_singular": None,
            "plural": None,
        }
        gender = None
        # Use regular expressions to extract the relevant information
        pattern = r"(.*?) \((.*?)\) \u00b7 Genitiv Singular: (.*?) \u00b7 Nominativ Plural: (.*)"
        match_elements = re.match(
            pattern=pattern, string=input_string, flags=re.UNICODE
        )
        if match_elements:
            # Update the dictionary with the extracted values
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
                else None
            )
        return data_dict

    def get_info(self):
        """Get detailed information about the word"""
        # Extracting word and article(s) for the word
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
