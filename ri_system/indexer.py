import nltk
import numpy as np
from nltk.corpus import stopwords
from pyuca import Collator

from ri_system.utilities import Utilities


class Indexer:
    def retrieve_html_str_terms(self, html_str, long, special, dash):
        tokens = self.apply_general_rules(html_str)

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
                            # Regla de extraer términos de tamaño máximo 30
                            if len(token) <= Utilities.max_term_length:
                                terms.append(token)
                            else:
                                long.append(token)
                    else:
                        # Caso del token que tiene guiones. Se verifica si es una excepción y si lo es se pone
                        # sin modificar en la lista de términos.
                        # Si no lo es, se divide en el guion y se ponen ambas partes en la lista de tokens por procesar
                        if Utilities.is_dashed_word_exception(token):
                            token = token.replace('-', '')
                            # Regla de extraer términos de tamaño máximo 30
                            if len(token) <= Utilities.max_term_length:
                                terms.append(token)
                            else:
                                long.append(token)
                        else:
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
                    else:
                        special.append('{:50} {}'.format(token, token.encode('utf-8')))

        return terms

    def process_collection(self, document_entries, collection_handler, debug):
        collection_handler.create_tok_dir()
        vocabulary = dict()
        collator = Collator()

        # TODO: pruebas
        if debug:
            long_file_lines = list()
            special_file_lines = list()
            dash_file_lines = list()
            terms_per_document_sum = 0

        for document_entry in document_entries:
            print(document_entry.get_alias())

            # TODO: pruebas
            if debug:
                long = list()
                special = list()
                dash = list()

            document_html_str = document_entry.get_html_str()
            document_terms = self.retrieve_html_str_terms(document_html_str, long, special, dash)
            tok_file_lines = list()

            if len(document_terms) > 0:
                if debug:
                    # prueba de promedio
                    terms_per_document_sum += len(document_terms)

                document_terms_np_array = np.array(document_terms)

                terms, counts = np.unique(document_terms_np_array, return_counts=True)
                max_l_freq_lj = max(counts)

                # El archivo tok debe estar ordenado alfabéticamente
                for term_ind, term in enumerate(sorted(terms, key=collator.sort_key)):
                    freq_ij = counts[term_ind]  # freq_ij = la frecuencia del término k_i en el documento d_j
                    f_ij = freq_ij / max_l_freq_lj  # f_ij = la frecuencia normalizada del término k_i en el documento d_j.
                    # Se calcula como freq_ij divido por la frecuencia del término más frecuente en el documento d_j
                    line = '{:30} {:12} {:20}'.format(term, str(freq_ij), str(f_ij))
                    tok_file_lines.append(line)
                    self.update_vocabulary_dict(vocabulary, term, freq_ij)
            else:
                print(document_entry.get_alias())
                tok_file_lines.append('\n')

            # TODO: PRUEBAS
            if debug:
                for long_elem in long:
                    line = '{:35} {}'.format(document_entry.get_alias(), long_elem)
                    long_file_lines.append(line)
    
                for special_elem in special:
                    line = '{:35} {}'.format(document_entry.get_alias(), special_elem)
                    special_file_lines.append(line)

                for dash_elem in dash:
                    line = '{:35} {}'.format(document_entry.get_alias(), dash_elem)
                    dash_file_lines.append(line)

            collection_handler.create_tok_file(document_entry.get_alias(), tok_file_lines)

        vocabulary_file_lines = list()

        # El archivo Vocabulario debe estar ordenado alfabéticamente
        for term in sorted(vocabulary.keys(), key=collator.sort_key):
            values_tuple = vocabulary[term]
            doc_count = values_tuple[0]
            col_freq_count = values_tuple[1]
            line = '{:30} {:12} {:20}'.format(term, str(doc_count), str(col_freq_count))
            vocabulary_file_lines.append(line)

        collection_handler.create_vocabulary_file(vocabulary_file_lines)

        # TODO: PRUEBAS
        if debug:
            print("La cantidad de palabras en el vocabulario es: ", len(vocabulary_file_lines))
            print("La cantidad promedio de palabras por documento es de: ", terms_per_document_sum/len(document_entries), " palabras.")
            print("La cantidad de palabras en long es: ", len(long_file_lines))
            print("La cantidad de palabras en special es: ", len(special_file_lines))
            print("La cantidad de palabras en dash es: ", len(dash_file_lines))

            long_file_str = '\n'.join(line for line in long_file_lines)
            Utilities.create_and_save_file('long.txt', long_file_str)

            special_file_str = '\n'.join(line for line in special_file_lines)
            Utilities.create_and_save_file('special.txt', special_file_str)

            dash_file_str = '\n'.join(line for line in dash_file_lines)
            Utilities.create_and_save_file('dash.txt', dash_file_str)

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

    @staticmethod
    def update_vocabulary_dict(vocabulary, term, count):
        if term in vocabulary.keys():
            vocabulary[term] = (vocabulary[term][0] + 1, vocabulary[term][1] + count)
        else:
            vocabulary[term] = (1, count)

    ########################
    # Funciones para pruebas
    ########################
    def process_html_str(self, html_str):
        long = list()
        special = list()
        terms = self.retrieve_html_str_terms(html_str, long, special)
        processed_html_string = '\n'.join(term for term in terms)
        return processed_html_string
