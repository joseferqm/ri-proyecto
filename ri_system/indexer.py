import numpy as np
from pyuca import Collator


from ri_system.analyzer import Analyzer
from ri_system.utilities import Utilities
import os


class Indexer:
    def __init__(self, collection_handler):
        self.__collection_handler = collection_handler

    def process_collection(self, document_entries, debug):
        self.__collection_handler.create_tok_dir()
        vocabulary = dict()
        collator = Collator()

        if debug:
            long_file_lines = list()
            special_file_lines = list()
            dash_file_lines = list()
            terms_per_document_sum = 0

        for document_entry in document_entries:
            document_html_str = document_entry.get_html_str()
            tok_file_lines = list()
            if debug:
                print('Procesando {}...'.format(document_entry.get_alias()))
                long = list()
                special = list()
                dash = list()
                document_terms = Analyzer.retrieve_html_str_terms(document_html_str, long, special, dash)
            else:
                document_terms = Analyzer.retrieve_html_str_terms(document_html_str)

            if len(document_terms) > 0:
                if debug:
                    # prueba de promedio
                    terms_per_document_sum += len(document_terms)

                document_terms_np_array = np.array(document_terms)

                terms, counts = np.unique(document_terms_np_array, return_counts=True)
                doc_vocabulary = dict(zip(terms, counts))
                max_l_freq_lj = max(counts)

                # El archivo tok debe estar ordenado alfabéticamente
                for term in sorted(doc_vocabulary.keys(), key=collator.sort_key):
                    freq_ij = doc_vocabulary[term]  # freq_ij = la frecuencia del término k_i en el documento d_j
                    f_ij = freq_ij / max_l_freq_lj  # f_ij = la frecuencia normalizada del término k_i en el documento d_j.
                    # Se calcula como freq_ij divido por la frecuencia del término más frecuente en el documento d_j
                    line = '{:30} {:12} {:20}'.format(term, str(freq_ij), str(round(f_ij, 3)))
                    tok_file_lines.append(line)
                    self.update_vocabulary_dict(vocabulary, term, freq_ij)
            else:
                tok_file_lines.append('\n')

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

            self.__collection_handler.create_tok_file(document_entry.get_alias(), tok_file_lines)

        vocabulary_file_lines = list()

        # El archivo Vocabulario debe estar ordenado alfabéticamente
        for term in sorted(vocabulary.keys(), key=collator.sort_key):
            values_tuple = vocabulary[term]
            doc_count = values_tuple[0]
            col_freq_count = values_tuple[1]
            line = '{:30} {:12} {:20}'.format(term, str(doc_count), str(col_freq_count))
            vocabulary_file_lines.append(line)

        self.__collection_handler.create_vocabulary_file(vocabulary_file_lines)

        if debug:
            Utilities.print_debug_header('Resultados de la indexación', True)
            print("La cantidad de palabras en el vocabulario es: ", len(vocabulary_file_lines))
            print("La cantidad promedio de palabras por documento es de: ",
                  terms_per_document_sum / len(document_entries), " palabras.")
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
    def update_vocabulary_dict(vocabulary, term, count):
        if term in vocabulary.keys():
            vocabulary[term] = (vocabulary[term][0] + 1, vocabulary[term][1] + count)
        else:
            vocabulary[term] = (1, count)
