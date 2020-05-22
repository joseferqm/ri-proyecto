from ri_system.collection_handler import CollectionHandler
from ri_system.indexer import Indexer
from ri_system.utilities import Utilities


class System:
    def __init__(self, debug):
        main_dir = 'RI_Coleccion'
        urls_file_name = 'URLS.txt'
        vocabulary_file_name = 'Vocabulario'
        html_files_dir = 'Coleccion'
        tok_files_dir = 'Coleccion_tok'

        self.__collection_handler = CollectionHandler(main_dir, urls_file_name, vocabulary_file_name,
                                                      html_files_dir, tok_files_dir)
        self.__indexer: Indexer = Indexer(self.__collection_handler)

        self.__document_entries = None

        self.__debug = debug

        if self.__debug:
            Utilities.print_debug_header('Modo debug')

    def prepare_collection(self):
        if self.__debug:
            Utilities.print_debug_header('Preparando la colección', True)

        self.__document_entries = self.__collection_handler.get_html_strings_and_urls_stream(self.__debug)

    def index_collection(self):
        if self.__debug:
            Utilities.print_debug_header('Indexando la colección', True)

        self.__indexer.process_collection(self.__document_entries, self.__debug)

    ########################
    # Funciones para pruebas
    ########################
    def index_random_document(self):
        html_string = self.__collection_handler.get_random_html_string()
        processed_html_string = self.__indexer.process_html_str(html_string)
        Utilities.create_and_save_file('original.html', html_string)
        Utilities.create_and_save_file('processed.txt', processed_html_string)

    def index_document(self, file_name):
        html_string = self.__collection_handler.get_html_string(file_name)
        processed_html_string = self.__indexer.process_html_str(html_string)
        Utilities.create_and_save_file('original.html', html_string)
        Utilities.create_and_save_file('processed.txt', processed_html_string)
