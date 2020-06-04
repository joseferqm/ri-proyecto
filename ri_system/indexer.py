import math

import numpy as np
from pyuca import Collator

from ri_system.analyzer import Analyzer
from ri_system.ouput_files import CollectionOutputFiles, DocumentOutputFiles
from ri_system.utilities import Utilities


class Indexer:
    def __init__(self, collection_handler):
        self.__collection_handler = collection_handler

    def process_collection(self, document_entries, debug):
        self.__collection_handler.create_tok_dir()
        self.__collection_handler.create_wtd_dir()
        vocabulary = dict()
        documents = dict()
        collator = Collator()

        if debug:
            long_file_lines = list()
            special_file_lines = list()
            dash_file_lines = list()
            terms_per_document_sum = 0

        for document_entry in document_entries:
            document_alias = document_entry.get_alias()
            documents[document_alias] = dict()
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
                    documents[document_alias][term] = round(f_ij, 3)
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

            self.__collection_handler.create_file_for_document(document_entry.get_alias(), tok_file_lines,
                                                               DocumentOutputFiles.TOK)

        vocabulary_file_lines = list()

        # El archivo Vocabulario debe estar ordenado alfabéticamente
        for term in sorted(vocabulary.keys(), key=collator.sort_key):
            values_tuple = vocabulary[term]
            n_i = values_tuple[0]
            idf = round(math.log10(len(document_entries) / n_i), 3)
            vocabulary[term] = (vocabulary[term][0], vocabulary[term][1], idf)
            line = '{:30} {:12} {:20}'.format(term, str(n_i), str(idf))
            vocabulary_file_lines.append(line)

        self.__collection_handler.create_file_for_collection(vocabulary_file_lines, CollectionOutputFiles.VOCABULARY)

        # Archivos Indice y Postings
        current_postings_line = 1
        postings_file_lines = list()
        index_file_lines = list()
        index_file_vocabulary = dict()
        for document_alias, document_terms in documents.items():
            wtd_file_lines = list()
            for term, f_ij in document_terms.items():
                weight = round(f_ij * vocabulary[term][2], 3)
                line = '{:30} {:20}'.format(term, str(weight))
                wtd_file_lines.append(line)
                line = '{:30} {:30} {:20}'.format(term, document_alias, str(weight))
                postings_file_lines.append(line)
                Indexer.update_index_dict(index_file_vocabulary, term, current_postings_line)
                current_postings_line += 1
            self.__collection_handler.create_file_for_document(document_alias, wtd_file_lines, DocumentOutputFiles.WTD)

        for term in sorted(index_file_vocabulary.keys(), key=collator.sort_key):
            values_tuple = index_file_vocabulary[term]
            postings_entries_count = values_tuple[0]
            postings_initial_position = values_tuple[1]
            line = '{:30} {:12} {:12}'.format(term, str(postings_initial_position), str(postings_entries_count))
            index_file_lines.append(line)

        self.__collection_handler.create_file_for_collection(index_file_lines, CollectionOutputFiles.INDEX)
        self.__collection_handler.create_file_for_collection(postings_file_lines, CollectionOutputFiles.POSTINGS)

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
            vocabulary[term] = (vocabulary[term][0] + 1, vocabulary[term][1] + count, vocabulary[term][2])
        else:
            vocabulary[term] = (1, count, None)

    @staticmethod
    def update_index_dict(vocabulary, term, current_postings_line):
        if term in vocabulary.keys():
            vocabulary[term] = (vocabulary[term][0] + 1, vocabulary[term][1])
        else:
            vocabulary[term] = (1, current_postings_line)
