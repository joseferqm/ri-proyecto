import os
import numpy as np

from ri_system.document_entry import DocumentEntry
from ri_system.ouput_files import CollectionOutputFiles, DocumentOutputFiles
from ri_system.utilities import Utilities


class CollectionHandler:
    def __init__(self):
        self.__main_dir = None
        self.__html_files_dir = None
        self.__urls_file_name = None
        self.__tok_files_dir = None
        self.__wtd_files_dir = None
        self.__vocabulary_file_name = None
        self.__index_file_name = None
        self.__postings_file_name = None

    def set_inputs_names(self, main_dir, urls_file_name, html_files_dir):
        self.__main_dir = main_dir
        self.__html_files_dir = html_files_dir
        self.__urls_file_name = urls_file_name

    def set_outputs_names(self, tok_files_dir, wtd_files_dir, vocabulary_file_name, index_file_name,
                          postings_file_name):
        self.__tok_files_dir = tok_files_dir
        self.__wtd_files_dir = wtd_files_dir
        self.__vocabulary_file_name = vocabulary_file_name
        self.__index_file_name = index_file_name
        self.__postings_file_name = postings_file_name

    def get_html_strings_and_urls_stream(self, debug):
        document_entries = list()

        urls_file_path = '{}/{}'.format(self.__main_dir, self.__urls_file_name)

        if debug:
            print('Leyendo {}...'.format(self.__urls_file_name))

        with Utilities.get_file(urls_file_path) as urls_file:
            for ind, line in enumerate(urls_file):
                # Para evitar errores, se eliminan caracteres de formato de Unicode
                line = Utilities.remove_unicode_format_chars(line)

                # Se elimina el caracter de nueva línea
                line = line.replace('\n', '')

                if debug:
                    print('Línea: {}'.format(line))

                # Al separar las líneas por espacios en blanco, el primer elemento de la tupla corresponde
                # al nombre del archivo en la colección
                line_elems = line.split(' ')
                html_file_name = line_elems[0]
                alias = html_file_name.replace('.html', '')

                if debug:
                    print('Leyendo {}...'.format(html_file_name))

                html_str = self.get_html_string(html_file_name)
                # TODO manejar urls
                url = line_elems[1]

                document_entry = DocumentEntry(alias, html_str, url)
                document_entries.append(document_entry)

        # No es necesario llamar close sobre los archivos porque el contexto en el que está definido cada archivo
        # se encarga de cerrarlo

        return document_entries

    def get_html_string(self, html_reference, reference_is_html_file_name=True):
        if reference_is_html_file_name:
            html_file_path = '{}/{}/{}'.format(self.__main_dir, self.__html_files_dir, html_reference)
        else:
            html_file_path = html_reference

        with Utilities.get_file(html_file_path) as html_file:
            html_str = Utilities.read_html_file(html_file, html_file_path)

        # No es necesario llamar close sobre los archivos porque el contexto en el que está definido cada archivo
        # se encarga de cerrarlo

        return html_str

    def create_file_for_document(self, document_entry_alias, lines, file_selector):
        if file_selector == DocumentOutputFiles.TOK:
            files_dir = self.__tok_files_dir
            file_extension = 'tok'
        elif file_selector == DocumentOutputFiles.WTD:
            files_dir = self.__wtd_files_dir
            file_extension = 'wtd'

        file_path = '{}/{}/{}.{}'.format(self.__main_dir, files_dir, document_entry_alias, file_extension)
        file_str = '\n'.join(line for line in lines)
        Utilities.create_and_save_file(file_path, file_str)

    def create_file_for_collection(self, lines, file_selector):
        if file_selector == CollectionOutputFiles.VOCABULARY:
            file_name = self.__vocabulary_file_name
        elif file_selector == CollectionOutputFiles.POSTINGS:
            file_name = self.__postings_file_name
        elif file_selector == CollectionOutputFiles.INDEX:
            file_name = self.__index_file_name

        file_path = '{}/{}'.format(self.__main_dir, file_name)
        file_str = '\n'.join(line for line in lines)
        Utilities.create_and_save_file(file_path, file_str)

    def create_tok_dir(self):
        if not os.path.isdir('{}/{}'.format(self.__main_dir, self.__tok_files_dir)):
            os.mkdir('{}/{}'.format(self.__main_dir, self.__tok_files_dir))

    def create_wtd_dir(self):
        if not os.path.isdir('{}/{}'.format(self.__main_dir, self.__wtd_files_dir)):
            os.mkdir('{}/{}'.format(self.__main_dir, self.__wtd_files_dir))

    def get_vocabulary_entries(self):
        vocabulary = dict()

        vocabulary_file_path = '{}/{}'.format(self.__main_dir, self.__vocabulary_file_name)

        with Utilities.get_file(vocabulary_file_path) as vocabulary_file:
            for line in vocabulary_file:
                # Formato de salida de Vocabulario.txt
                #   Primeros 30 caracteres -> término
                #   Últimos 20 caracteres -> idf del término
                line = line.replace('\n', '')
                term = line[:30].replace(' ', '')
                term_idf = float(line[-20:].replace(' ', ''))

                vocabulary[term] = term_idf

        return vocabulary

    def get_postings_lists(self, terms):
        index_results = dict()
        postings_lists = dict()

        index_file_path = '{}/{}'.format(self.__main_dir, self.__index_file_name)
        postings_file_path = '{}/{}'.format(self.__main_dir, self.__postings_file_name)

        with Utilities.get_file(index_file_path) as index_file:
            for line in index_file:
                # Formato de salida de Indice.txt
                #   Primeros 30 caracteres -> término
                #   Siguientes 12 caracteres -> posición inicial en archivo postings
                #   Últimos 12 caracteres -> cantidad de entradas en archivo postings
                line = line.replace('\n', '')
                term = line[:30].replace(' ', '')

                if term in terms:
                    initial_position = int(line[31:43].replace(' ', ''))
                    entries_count = int(line[-12:].replace(' ', ''))

                    index_results[term] = (initial_position, entries_count)

        with Utilities.get_file(postings_file_path) as postings_file:
            postings_file_lines = postings_file.read().splitlines()
            for term in terms:
                postings_lists[term] = list()

                index_results_info_tuple = index_results[term]
                current_position = index_results_info_tuple[0]
                entries_count = index_results_info_tuple[1]

                while entries_count > 0:
                    # Formato de salida de Postings.txt
                    #   Primeros 30 caracteres -> término
                    #   Siguientes 40 caracteres -> alias del documento
                    #   Últimos 20 caracteres -> peso del término en el documento
                    current_line = postings_file_lines[current_position]
                    document_alias = current_line[31:71].replace(' ', '')
                    term_weight = float(current_line[-20:].replace(' ', ''))

                    postings_lists[term].append((document_alias, term_weight))

                    current_position += 1
                    entries_count -= 1

        return postings_lists

    def get_documents_weights_full_vectors(self, documents):
        documents_vectors = list()

        for document_alias in documents:
            wtd_file_name = document_alias.replace('html', 'wtd')
            wtd_file_path = '{}/{}/{}'.format(self.__main_dir, self.__wtd_files_dir, wtd_file_name)
            with Utilities.get_file(wtd_file_path) as wtd_file:
                document_vector = list()
                for line in wtd_file:
                    # Formato de salida de .wtd
                    #   Primeros 30 caracteres -> término
                    #   Últimos 20 caracteres -> peso del término
                    term_weight = float(line[-20:].replace(' ', ''))
                    document_vector.append(term_weight)

                document_vector_np_array = np.array(document_vector)
                documents_vectors.append(document_vector_np_array)

        return documents_vectors
