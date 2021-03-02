from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords, wordnet
import re
from typing import List, Dict
import unicodedata


class TextProcessor:
    """Custom class used to prepare word frequencies for creation of wordcloud."""

    def __init__(self, stopwords: List[str] = stopwords.words("english")):
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = stopwords

    def tokenize_and_normalize(self, text: str) -> List[str]:
        """Normalize and tokenize text using WordNet lemmatizer."""
        tokenized_text = []
        for token, tag in pos_tag(word_tokenize(text)):
            lemma = self.lemmatizer.lemmatize(self.strip(token).lower(), self._get_wn_tag(tag))
            if self.is_valid_token(lemma):
                tokenized_text.append(lemma)

        return tokenized_text

    def is_valid_token(self, token: str) -> bool:
        """Invalid tokens are stopwords and punctuation marks in this usecase."""
        return self.is_latin(token) and not (
            self.is_stopword(token) or self.is_punct(token) or self.is_digit(token) or self.is_single_letter(token)
        )

    def is_stopword(self, token: str) -> bool:
        return self.strip(token).lower() in self.stopwords

    def is_punct(self, token: str) -> bool:
        return all(unicodedata.category(char).startswith("P") for char in self.strip(token))

    def is_latin(self, token: str) -> bool:
        """We want to have only words in latin alphabet in wordcloud."""
        return bool(re.match("\w", self.strip(token)))

    def is_digit(self, token: str) -> bool:
        return bool(re.match("\d+", self.strip(token)))

    def is_single_letter(self, token: str) -> bool:
        """Sometimes people use single letter abbreviations instead of full word, e.g. 'u' instead of 'you'."""
        return len(self.strip(token)) == 1

    @staticmethod
    def strip(string: str) -> str:
        return string.strip().strip("'")

    @staticmethod
    def _get_wn_tag(tag: str) -> str:
        if tag.startswith("NN"):
            return wordnet.NOUN
        if tag.startswith("VB"):
            return wordnet.VERB
        if tag.startswith("JJ"):
            return wordnet.ADJ
        if tag.startswith("RB"):
            return wordnet.ADV
        return wordnet.NOUN

    @staticmethod
    def get_word_frequencies(tokenized_docs: List[List[str]]) -> Dict[str, int]:
        """Creates dictionary with keys being lemmas and values being frequencies
        of said lemmas."""
        frequencies = {}
        for doc in tokenized_docs:
            for token in doc:
                if token in frequencies.keys():
                    frequencies[token] += 1
                else:
                    frequencies[token] = 1

        return frequencies
