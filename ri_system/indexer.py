import nltk
import numpy as np
from nltk.corpus import stopwords

from ri_system.utilities import Utilities


class Indexer:
    def retrieve_html_str_terms(self, html_str):
        tokens = self.apply_general_rules(html_str)

        # TODO: Por ahora se incluyen los guiones en la lista de caracteres admitidos
        # TODO: Manejar excepciones de palabras con guiones
        terms = list()

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
                    terms.append(str(number))
            else:
                if Utilities.has_only_allowed_chars(token):
                    # Caso del token que solo tiene caracteres permitidos
                    if '-' not in token:
                        # Caso del token que no tiene guiones. Se verifica si no es stop word
                        # y se pone en la lista de términos
                        if token not in stopwords.words('spanish'):
                            terms.append(token)
                    else:
                        # Caso del token que tiene guiones. Se verifica si es una excepción y si lo es se pone
                        # sin modificar en la lista de términos.
                        # Si no lo es, se divide en el guion y se ponen ambas partes en la lista de tokens por procesar
                        if Utilities.is_dashed_word_exception(token):
                            terms.append(token)
                        else:
                            sub_tokens = token.split('-')
                            for sub_token in sub_tokens:
                                tokens.append(sub_token)
                else:
                    # Caso del token que tiene caracteres no permitidos. Se transforma y si ahora solo tiene
                    # caracteres permitidos, se pone modificado en la lista de tokens por procesar
                    norm_token = Utilities.normalize_special_chars(token)
                    if Utilities.has_only_allowed_chars(norm_token):
                        tokens.append(norm_token)
                    else:
                        print('\t{}'.format(token))
                        print('\t{}'.format(token.encode('utf-8')))

            # else:
            #     # Se imprimen primero los términos que se excluyen
            #     print(token)
            #     print(token.encode('utf-8'))

        return terms

    def process_collection(self, document_entries, collection_handler):
        collection_handler.create_tok_dir()
        vocabulary = dict()

        for document_entry in document_entries:
            print(document_entry.get_alias())
            document_html_str = document_entry.get_html_str()
            document_terms = self.retrieve_html_str_terms(document_html_str)
            tok_file_lines = list()

            if len(document_terms) > 0:
                document_terms_np_array = np.array(document_terms)
                # El archivo tok debe estar ordenado alfabéticamente
                # unique returns the sorted unique elements of an array
                terms, counts = np.unique(document_terms_np_array, return_counts=True)
                max_l_freq_lj = max(counts)

                for term_ind, term in enumerate(terms):
                    freq_ij = counts[term_ind]  # freq_ij = la frecuencia del término k_i en el documento d_j
                    f_ij = freq_ij / max_l_freq_lj  # f_ij = la frecuencia normalizada del término k_i en el documento d_j.
                    # Se calcula como freq_ij divido por la frecuencia del término más frecuente en el documento d_j
                    line = '{} {} {}'.format(term, freq_ij, f_ij)
                    tok_file_lines.append(line)
                    self.update_vocabulary_dict(vocabulary, term, freq_ij)
            else:
                print(document_entry.get_alias())
                tok_file_lines.append('\n')

            collection_handler.create_tok_file(document_entry.get_alias(), tok_file_lines)

        vocabulary_file_lines = list()

        # El archivo Vocabulario debe estar ordenado alfabéticamente
        for term, values_tuple in sorted(vocabulary.items()):
            doc_count = values_tuple[0]
            col_freq_count = values_tuple[1]
            line = '{} {} {}'.format(term, doc_count, col_freq_count)
            vocabulary_file_lines.append(line)

        collection_handler.create_vocabulary_file(vocabulary_file_lines)

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

        # # Regla: Eliminar algunos caracteres especiales de unicode
        text = Utilities.replace_unicode_format_chars(text)

        # Regla: Eliminar espacios en blanco
        tokens = nltk.word_tokenize(text)

        return tokens

    @staticmethod
    def update_vocabulary_dict(vocabulary, term, count):
        if term in vocabulary.keys():
            vocabulary[term] = (vocabulary[term][0] + 1, vocabulary[term][1] + count)
        else:
            vocabulary[term] = (1, count)

    ########################
    # Funciones para pruebas
    ########################
    def create_hyphenated_terms_file(self, html_strings_stream):
        hyphenated_terms = set()

        for html_str in html_strings_stream:
            tokens = self.apply_general_rules(html_str)

            for token in tokens:
                token = Utilities.handle_dash_chars(token)

                if token and Utilities.has_only_allowed_chars(token) and '-' in token:
                    hyphenated_terms.add(token)

        hyphenated_terms_list = list(hyphenated_terms)
        hyphenated_terms_list.sort()

        hyphenated_terms_string = '\n'.join(hyphenated_term for hyphenated_term in hyphenated_terms_list)

        Utilities.create_and_save_file('hyphenated_terms.txt', hyphenated_terms_string)

    def process_html_str(self, html_str):
        terms = self.retrieve_html_str_terms(html_str)
        processed_html_string = '\n'.join(term for term in terms)
        return processed_html_string
