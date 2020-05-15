from ri_system.collection_handler import CollectionHandler
from ri_system.indexer import Indexer
from ri_system.utilities import Utilities


class System:
    def __init__(self):
        main_dir = 'RI_Coleccion'
        urls_file_name = 'URLS.txt'
        vocabulary_file_name = 'Vocabulario'
        html_files_dir = 'Coleccion'
        tok_files_dir = 'Coleccion_tok'

        self.__collection_handler = CollectionHandler(main_dir, urls_file_name, vocabulary_file_name,
                                                      html_files_dir, tok_files_dir)
        self.__indexer = Indexer()

        self.__document_entries = None

    def prepare_collection(self):
        self.__document_entries = self.__collection_handler.get_html_strings_and_urls_stream()

    def index_collection(self):
        self.__indexer.process_collection(self.__document_entries, self.__collection_handler)

    ########################
    # Funciones para pruebas
    ########################
    def create_hyphenated_terms_file(self):
        self.__indexer.create_hyphenated_terms_file(self.__document_entries)

    def index_random_document(self):
        try:
            html_string = self.__collection_handler.get_random_html_string()
            processed_html_string = self.__indexer.process_html_str(html_string)
            Utilities.create_and_save_file('original.html', html_string)
            Utilities.create_and_save_file('processed.txt', processed_html_string)
        except Exception as e:
            print('Excepción tipo {}:\t{}'.format(type(e), e))

    def index_document(self, file_name):
        try:
            html_string = self.__collection_handler.get_html_string(file_name)
            processed_html_string = self.__indexer.process_html_str(html_string)
            Utilities.create_and_save_file('original.html', html_string)
            Utilities.create_and_save_file('processed.txt', processed_html_string)
        except Exception as e:
            print('Excepción tipo {}:\t{}'.format(type(e), e))
