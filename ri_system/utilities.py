import io
import re
import string
import unicodedata

import regex
from bs4 import BeautifulSoup, Comment


class Utilities:
    # https://www.regular-expressions.info/unicode.html
    # \p{C} or \p{Other}: invisible control characters and unused code points.
    # \p{Cf} or \p{Format}: invisible formatting indicator.
    # \p{P} or \p{Punctuation}: any kind of punctuation character.
    # \p{Pd} or \p{Dash_Punctuation}: any kind of hyphen or dash.

    regex_all_other_chars = regex.compile('\p{Other}')
    regex_format_chars = regex.compile('\p{Format}')
    # Se debe hacer de esta manera porque [\p{Punctuation}--\p{Dash_Punctuation}] no funciona
    regex_punctuation_chars = regex.compile(
        '[\p{Symbol}&&\p{Open_Punctuation}&&\p{Close_Punctuation}&&\p{Initial_Punctuation}&&\p{Final_Punctuation}&&\p{Connector_Punctuation}&&\p{Other_Punctuation}]'
    )
    regex_dash_chars = regex.compile('\p{Dash_Punctuation}')
    regex_digit_chars = regex.compile('\p{Digit}')

    additional_chars = ['á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ', '-']
    allowed_chars = string.digits + string.ascii_lowercase + ''.join(c for c in additional_chars)
    regex_allowed_chars = re.compile('[' + allowed_chars + ']')

    # Colección de prefijos para palabras con guion que son excepciones
    dash_exceptions = ['pre-', 'post-', 'pos-', 'sub-', 'ex-', 'anti-', 'pro-', 'súper-', 'super-', 'co-']

    max_term_length = 30
    min_number = 0
    max_number = 10000

    @staticmethod
    def get_file(file_path):
        return open(file_path, encoding='utf-8-sig')

    @staticmethod
    def create_and_save_file(file_path, text):
        f = open(file_path, 'w', encoding='utf-8')
        f.write(text)
        f.close()

    @staticmethod
    def read_html_file(file, file_path):
        try:
            return file.read()
        except UnicodeError:
            pass
        alternative_file = io.open(file_path, encoding='latin-1')
        return alternative_file.read()

    @staticmethod
    def replace_unicode_all_other_chars(original_str):
        return Utilities.handle_group_chars(Utilities.regex_all_other_chars, original_str, ' ')

    @staticmethod
    def remove_unicode_format_chars(original_str):
        return Utilities.handle_group_chars(Utilities.regex_format_chars, original_str)

    @staticmethod
    def replace_punctuation_chars(original_str):
        return Utilities.handle_group_chars(Utilities.regex_punctuation_chars, original_str, ' ')

    @staticmethod
    def handle_group_chars(group, original_str, replacement_char=''):
        return regex.sub(group, replacement_char, original_str)

    @staticmethod
    def normalize_dash_chars(original_str):
        # Remplazar todos los que sean Dash_Punctuation por '-'
        normalized_str = regex.sub(Utilities.regex_dash_chars, '-', original_str)

        # Reemplazar los grupos de repetidos leading
        normalized_str = re.sub(r'(\s+[\-]+)([\S]+)', r' -\2', normalized_str)

        # Reemplazar los grupos de repetidos en medio y trailing
        normalized_str = re.sub(r'([^\s\-]+)([\-]+)', r'\1-', normalized_str)

        return normalized_str

    @staticmethod
    def handle_dash_chars(original_str):
        # Eliminar leading y trailing
        return original_str.strip('-')

    @staticmethod
    def is_dashed_word_exception(term):
        if term.count('-') == 1 and any(term.startswith(x) for x in Utilities.dash_exceptions):
            return True
        return False

    @staticmethod
    def in_range(number):
        return Utilities.min_number <= number <= Utilities.max_number

    @staticmethod
    def has_only_digits(term):
        for char in term:
            if not regex.match(Utilities.regex_digit_chars, char):
                return False
        return True

    @staticmethod
    def has_only_allowed_chars(term):
        for char in term:
            if not re.match(Utilities.regex_allowed_chars, char):
                return False
        return True

    @staticmethod
    def normalize_special_chars(original_str):
        norm = unicodedata.normalize('NFKD', original_str)
        return ''.join(char for char in norm if not unicodedata.combining(char))

    @staticmethod
    def get_text_from_html_str(html_str):
        html_str = html_str.replace('>', '> ')

        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#beautifulsoup
        soup = BeautifulSoup(html_str, 'html.parser')

        # If you only want the text part of a document, you can use the get_text() method.
        # It returns all the text in a document as a single Unicode string.
        return soup.get_text()
