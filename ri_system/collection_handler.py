import glob
import os
import random

from ri_system.utilities import Utilities


class CollectionHandler:
    def __init__(self, main_dir, urls_file_name, html_files_dir):
        self.__main_dir = main_dir
        self.__urls_file_name = urls_file_name
        self.__html_files_dir = html_files_dir

    def get_html_strings_and_urls_stream(self):
        strings_stream = list()
        urls_stream = list()

        urls_file_path = '{}/{}'.format(self.__main_dir, self.__urls_file_name)

        try:
            with Utilities.get_file(urls_file_path) as urls_file:
                for ind, line in enumerate(urls_file):
                    # Para evitar errores, se eliminan caracteres de formato de Unicode
                    line = Utilities.remove_unicode_format_chars(line)

                    # Se elimina el caracter de nueva línea
                    line = line.replace('\n', '')

                    # Al separar las líneas por espacios en blanco, el primer elemento de la tupla corresponde
                    # al nombre del archivo en la colección
                    line_elems = line.split(' ')
                    html_file_name = line_elems[0]
                    html_str = self.get_html_string(html_file_name)
                    html_url = line_elems[1]

                    strings_stream.append(html_str)
                    urls_stream.append(html_url)

            # No es necesario llamar close sobre los archivos porque el contexto en el que está definido cada archivo
            # se encarga de cerrarlo

            return strings_stream, urls_stream
        except Exception as e:
            print('Excepción tipo {}:\t{}'.format(type(e), e))

    def get_html_string(self, html_reference, reference_is_html_file_name=True):
        if reference_is_html_file_name:
            html_file_path = '{}/{}/{}'.format(self.__main_dir, self.__html_files_dir, html_reference)
        else:
            html_file_path = html_reference

        try:
            with Utilities.get_file(html_file_path) as html_file:
                html_str = Utilities.read_html_file(html_file, html_file_path)

            # No es necesario llamar close sobre los archivos porque el contexto en el que está definido cada archivo
            # se encarga de cerrarlo

            return html_str
        except Exception as e:
            print('Excepción tipo {}:\t{}'.format(type(e), e))

    def get_random_html_string(self):
        html_files_path = '{}/{}/{}'.format(os.getcwd(), self.__main_dir, self.__html_files_dir)
        html_files_vect = glob.glob('{}/*.html'.format(html_files_path))
        html_files_count = len(html_files_vect)
        rand = random.randint(0, html_files_count - 1)
        html_file_path = html_files_vect[rand]

        print(html_file_path)

        try:
            return self.get_html_string(html_file_path, False)
        except Exception as e:
            print('Excepción tipo {}:\t{}'.format(type(e), e))