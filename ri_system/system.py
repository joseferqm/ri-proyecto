import json
import os
import time
import tkinter
from tkinter import filedialog, messagebox

from ri_system.collection_handler import CollectionHandler
from ri_system.indexer import Indexer
from ri_system.search_engine import SearchEngine
from ri_system.utilities import Utilities


class System:
    def __init__(self, debug, search_engine):
        if search_engine:
            main_dir = "RI_Coleccion"
        else:
            root = tkinter.Tk()
            root.withdraw()
            main_dir = self.search_for_file_path(root)

        urls_file_name = 'URLS.txt'
        vocabulary_file_name = 'Vocabulario.txt'
        index_file_name = 'Indice.txt'
        postings_file_name = 'Postings.txt'
        html_files_dir = 'Coleccion'
        tok_files_dir = 'Coleccion_tok'
        wtd_files_dir = 'Coleccion_wtd'

        self.__collection_handler: CollectionHandler = CollectionHandler()
        self.__collection_handler.set_inputs_names(main_dir, urls_file_name, html_files_dir)
        self.__collection_handler.set_outputs_names(tok_files_dir, wtd_files_dir, vocabulary_file_name, index_file_name,
                                                    postings_file_name)
        self.__indexer: Indexer = Indexer(self.__collection_handler)
        self.__search_engine: SearchEngine = SearchEngine(self.__collection_handler)
        self.__document_entries = None

        self.__debug_mode = debug
        self.__search_engine_mode = search_engine
        self.__start = None
        self.__end = None

        if self.__debug_mode:
            Utilities.print_debug_header('Modo debug')

    def prepare_collection(self):
        if self.__debug_mode:
            self.__start = time.perf_counter()
            Utilities.print_debug_header('Preparando la colección', True)

        self.__document_entries = self.__collection_handler.get_html_strings_and_urls_stream(self.__debug_mode,
                                                                                             self.__search_engine_mode)

    def index_collection(self):
        if self.__debug_mode:
            Utilities.print_debug_header('Indexando la colección', True)

        self.__indexer.process_collection(self.__document_entries.values(), self.__debug_mode)

        if self.__debug_mode:
            self.__end = time.perf_counter()
            print(f"Tiempo de ejecución -> {self.__end - self.__start:0.4f} s")

        if not self.__search_engine_mode:
            messagebox.showinfo(message="main.exe: ejecución completada.", title="Información")

    def search_for_file_path(self, root):
        currdir = os.getcwd()
        tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Por favor seleccione un directorio')
        if len(tempdir) > 0:
            print("You chose: %s" % tempdir)
        return tempdir

    def execute_query(self, query_string):
        start = time.perf_counter()
        self.__search_engine.set_collection_vocabulary()
        ranked_documents = self.__search_engine.get_ranked_documents(query_string)
        query_results = dict()
        # print(os.getcwd())
        current_directory = os.getcwd()
        for index, document_complete_alias in enumerate(ranked_documents):
            document_alias = document_complete_alias.replace('.html', '')
            # print('{} -> {}'.format(document_alias, self.__document_entries[document_alias].get_url()))
            # query_results.append(self.__document_entries[document_alias])
            query_results[index] = dict([
                ('alias', self.__document_entries[document_alias].get_alias()),
                ('url', self.__document_entries[document_alias].get_url()),
                ('local', '{}/RI_Coleccion/Coleccion/{}'.format(current_directory, document_complete_alias))
            ])
            # print(query_results[index])

        end = time.perf_counter()
        query_time = f"{end - start:0.4f}"
        print("Tiempo de ejecución -> {} s".format(query_time))
        query_results['query_time'] = query_time
        print(query_results)
        return json.dumps(query_results)
