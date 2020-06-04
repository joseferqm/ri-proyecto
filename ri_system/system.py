import os
import tkinter
from tkinter import filedialog, messagebox

from ri_system.collection_handler import CollectionHandler
from ri_system.indexer import Indexer
from ri_system.utilities import Utilities


class System:
    def __init__(self, debug):

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

        self.__collection_handler = CollectionHandler()
        self.__collection_handler.set_inputs_names(main_dir, urls_file_name, html_files_dir)
        self.__collection_handler.set_outputs_names(tok_files_dir, wtd_files_dir, vocabulary_file_name, index_file_name,
                                                    postings_file_name)
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
        messagebox.showinfo(message="main.exe: ejecución completada.", title="Información")

    def search_for_file_path(self, root):
        currdir = os.getcwd()
        tempdir = filedialog.askdirectory(parent=root, initialdir=currdir, title='Por favor seleccione un directorio')
        if len(tempdir) > 0:
            print("You chose: %s" % tempdir)
        return tempdir
