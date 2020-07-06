import nltk
from nltk.corpus import stopwords

from ri_system.utilities import Utilities


class Analyzer:
    @staticmethod
    def retrieve_html_str_terms(html_str, long=None, special=None, dash=None):
        tokens = Analyzer.apply_general_rules(html_str)

        retrieved_terms = list()

        while tokens:
            token = tokens.pop()

            # Eliminar los guiones leading y trailing restantes
            token = Utilities.handle_dash_chars(token)

            # Ignorar si es hilera vacía
            if not token:
                continue

            if Utilities.has_only_digits(token):
                # Se intenta interpretar términos que corresponden a números solo como enteros positivos
                # porque separadores de decimales (y miles) se reemplazaron por espacios en blanco al manejar
                # caracteres de puntuación y porque rango inicia en 0
                number = int(token)
                if Utilities.in_range(number):
                    retrieved_terms.append(str(number))
            else:
                if Utilities.has_only_allowed_chars(token):
                    # Caso del token que solo tiene caracteres permitidos
                    if '-' not in token:
                        # Regla de extraer términos de tamaño máximo 30
                        if len(token) <= Utilities.max_term_length:
                            # Caso del token que no tiene guiones.
                            # Puede tener solo letras, o dígitos y letras,
                            # pero no tiene solo dígitos (porque el caso ya se controló).
                            # Si es un término con dígitos y letras, y no empieza con a-z no numérico, se separan
                            # grupos de dígitos y grupos de letras, y se ponen en la lista de tokens por procesar.
                            # Si no, se trata de un término que:
                            #   1) Tiene solo letras, o
                            #   2) Tiene dígitos y letras, e inicia con a-z no numérico
                            if token[0].isdigit():
                                groups = Utilities.get_digits_or_letters_groups(token)
                                for group in groups:
                                    tokens.append(group)
                            else:
                                # Se verifica si no es stop word
                                if token not in stopwords.words('spanish'):
                                    retrieved_terms.append(token)
                        elif long is not None:
                            long.append(token)
                    else:
                        # Caso del token que tiene guiones. Se verifica si es una excepción y si lo es se
                        # elimina el guion y se pone en la lista de términos.
                        # Si no lo es, se divide en el guion y se ponen las partes en la lista de tokens por procesar
                        if Utilities.is_dashed_word_exception(token):
                            token = token.replace('-', '')
                            # Regla de extraer términos de tamaño máximo 30
                            if len(token) <= Utilities.max_term_length:
                                retrieved_terms.append(token)
                            elif long is not None:
                                long.append(token)
                        else:
                            if dash is not None:
                                dash.append(token)

                            sub_tokens = token.split('-')
                            for sub_token in sub_tokens:
                                tokens.append(sub_token)
                else:
                    # Caso del token que tiene caracteres no permitidos. Se transforma y si ahora solo tiene
                    # caracteres permitidos, se pone modificado en la lista de tokens por procesar
                    norm_token = Utilities.normalize_special_chars(token)
                    if Utilities.has_only_allowed_chars(norm_token):
                        tokens.append(norm_token)
                    elif special is not None:
                        special.append('{:50} {}'.format(token, token.encode('utf-8')))

        return retrieved_terms

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
        text = Utilities.replace_punctuation_chars(text)

        # Regla: Eliminar algunos caracteres especiales de unicode
        # Ahora se reemplazarn todos los de control por espacios en blanco
        text = Utilities.replace_unicode_all_other_chars(text)

        # Regla: Eliminar espacios en blanco
        tokens = nltk.word_tokenize(text)

        return tokens
