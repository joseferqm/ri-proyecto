import io
import re
import string

import regex
from bs4 import BeautifulSoup


class Utilities:
    # https://www.regular-expressions.info/unicode.html
    # \p{Cf} or \p{Format}: invisible formatting indicator.
    # \p{P} or \p{Punctuation}: any kind of punctuation character.
    # \p{Pd} or \p{Dash_Punctuation}: any kind of hyphen or dash.

    regex_format_chars = regex.compile('\p{Format}')
    # Se debe hacer de esta manera porque [\p{Punctuation}--\p{Dash_Punctuation}] no funciona
    regex_punctuation_chars = regex.compile(
        '[\p{Symbol}&&\p{Open_Punctuation}&&\p{Close_Punctuation}&&\p{Initial_Punctuation}&&\p{Final_Punctuation}&&\p{Connector_Punctuation}&&\p{Other_Punctuation}]'
    )
    regex_dash_chars = regex.compile('\p{Dash_Punctuation}')

    additional_chars = ['á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ', '-']
    allowed_chars = string.digits + string.ascii_lowercase + ''.join(c for c in additional_chars)
    regex_allowed_chars = re.compile('[' + allowed_chars + ']')

    @staticmethod
    def get_file(file_path):
        return open(file_path)

    @staticmethod
    def create_and_save_file(file_path, text):
        f = open(file_path, 'w')
        f.write(text)
        f.close()

    @staticmethod
    def read_html_file(file, file_path):
        try:
            return file.read()
        except UnicodeError:
            pass
        try:
            alternative_file = io.open(file_path, encoding='latin-1')
            return alternative_file.read()
        except Exception:
            raise

    @staticmethod
    def remove_unicode_format_chars(original_str):
        return Utilities.handle_unicode_format_chars(original_str)

    @staticmethod
    def replace_unicode_format_chars(original_str):
        return Utilities.handle_unicode_format_chars(original_str, ' ')

    @staticmethod
    def handle_unicode_format_chars(original_str, replacement_char=''):
        return regex.sub(Utilities.regex_format_chars, replacement_char, original_str)

    @staticmethod
    def remove_punctuation_chars(original_str):
        return Utilities.handle_punctuation_chars(original_str)

    @staticmethod
    def replace_punctuation_chars(original_str):
        return Utilities.handle_punctuation_chars(original_str, ' ')

    @staticmethod
    def handle_punctuation_chars(original_str, replacement_char=''):
        return regex.sub(Utilities.regex_punctuation_chars, replacement_char, original_str)

    @staticmethod
    def normalize_dash_chars(original_str):
        return regex.sub(Utilities.regex_dash_chars, '-', original_str)

    @staticmethod
    def has_only_allowed_chars(term):
        for char in term:
            if not re.match(Utilities.regex_allowed_chars, char):
                return False
        return True

    @staticmethod
    def get_text_from_html_str(html_str):
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#beautifulsoup
        # If you only want the text part of a document, you can use the get_text() method.
        # It returns all the text in a document as a single Unicode string.
        soup = BeautifulSoup(html_str, 'lxml')
        return soup.get_text()
