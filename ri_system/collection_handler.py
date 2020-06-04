import os

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

    def create_vocabulary_file(self, lines):
        vocabulary_file_path = '{}/{}'.format(self.__main_dir, self.__vocabulary_file_name)
        vocabulary_file_str = '\n'.join(line for line in lines)
        Utilities.create_and_save_file(vocabulary_file_path, vocabulary_file_str)

    def create_tok_dir(self):
        if not os.path.isdir('{}/{}'.format(self.__main_dir, self.__tok_files_dir)):
            os.mkdir('{}/{}'.format(self.__main_dir, self.__tok_files_dir))

    def create_wtd_dir(self):
        if not os.path.isdir('{}/{}'.format(self.__main_dir, self.__wtd_files_dir)):
            os.mkdir('{}/{}'.format(self.__main_dir, self.__wtd_files_dir))
