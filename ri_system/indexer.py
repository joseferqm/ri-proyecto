import nltk

from ri_system.utilities import Utilities


class Indexer:
    def process_html_str(self, html_str):
        # TODO: Procesamiento de la hilera leída del archivo html
        tokens = self.apply_general_rules(html_str)

        # TODO: Por ahora se eliminan los términos si tienen caracteres que no correspondan a los admitidos
        # TODO: Por ahora se incluyen los guiones en la lista de caracteres admitidos
        # TODO: Manejar excepciones de palabras con guiones
        # TODO: Manejar stopwords
        terms = list()
        for token in tokens:
            token = Utilities.handle_dash_chars(token)

            if token and Utilities.has_only_allowed_chars(token):
                terms.append(token)
            else:
                # Se imprimen primero los términos que se excluyen
                print(token)
                print(token.encode('utf-8'))

        processed_html_string = '\n'.join(term for term in terms)

        return processed_html_string

    def process_collection(self, html_strings_stream):
        for html_str in html_strings_stream:
            processed_html_string = self.process_html_str(html_str)

    def create_hyphenated_terms_file(self, html_strings_stream):
        hyphenated_terms = set()

        for html_str in html_strings_stream:
            # TODO: Procesamiento de la hilera leída del archivo html
            tokens = self.apply_general_rules(html_str)

            for token in tokens:
                token = Utilities.handle_dash_chars(token)

                if token and Utilities.has_only_allowed_chars(token) and '-' in token:
                    hyphenated_terms.add(token)

        hyphenated_terms_list = list(hyphenated_terms)
        hyphenated_terms_list.sort()

        hyphenated_terms_string = '\n'.join(hyphenated_term for hyphenated_term in hyphenated_terms_list)

        try:
            Utilities.create_and_save_file('hyphenated_terms.txt', hyphenated_terms_string)
        except Exception as e:
            print('Excepción tipo {}:\t{}'.format(type(e), e))

    @staticmethod
    def apply_general_rules(html_str):
        # Regla: Eliminar etiquetas html
        text = Utilities.get_text_from_html_str(html_str)

        # Regla: Pasar los caracteres a minúsculas
        text = text.lower()

        # Regla: Utilizar el mismo caracter para los guiones
        text = Utilities.normalize_dash_chars(text)

        # Regla: Eliminar signos de puntuación y símbolos, y reemplazarlos por espacios en blanco
        # No se eliminan guiones porque se manejan tomando en cuenta excepciones
        # TODO: Al eliminar la puntuación, considerar casos en que puede ser separador decimal o de miles (. o , rodeado por números)
        text = Utilities.replace_punctuation_chars(text)

        # # Regla: Eliminar algunos caracteres especiales de unicode
        text = Utilities.replace_unicode_format_chars(text)

        # Regla: Eliminar espacios en blanco
        tokens = nltk.word_tokenize(text)

        return tokens
