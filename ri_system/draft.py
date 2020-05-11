import io
import re

import nltk
from bs4 import BeautifulSoup

ALLOWED_CHARS = list()


def get_file(filename):
    return open(filename)


def read_html_file(file, filename):
    try:
        return file.read()
    except UnicodeError:
        pass
    try:
        alternative_file = io.open(filename, encoding='latin-1')
        return alternative_file.read()
    except Exception:
        raise


def get_text_from_html_str(string):
    # http://2017.compciv.org/guide/topics/python-nonstandard-libraries/beautifulsoup.html
    # soup = BeautifulSoup(string, 'lxml')
    # return soup.text

    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#beautifulsoup
    # If you only want the text part of a document, you can use the get_text() method.
    # It returns all the text in a document as a single Unicode string.
    soup = BeautifulSoup(string, 'lxml')
    return soup.get_text()


def process_html_str(html_str):
    # TODO: Procesamiento de la hilera leída del archivo html
    return html_str


def define_unicode_allowed_chars():
    for char_value in range(ord('0'), ord('9') + 1):
        ALLOWED_CHARS.append(chr(char_value).encode('utf-8'))

    for char_value in range(ord('a'), ord('z') + 1):
        ALLOWED_CHARS.append(chr(char_value).encode('utf-8'))

    additional_chars = ['á', 'é', 'í', 'ó', 'ú', 'ü', 'ñ']

    for char in additional_chars:
        ALLOWED_CHARS.append(char.encode('utf-8'))


def include_term(string):
    for char in string:
        if char.encode('utf-8') not in ALLOWED_CHARS:
            return False
    return True


def process_urls_files(main_dir, urls_file_name, html_files_dir):
    urls_file_path = '{}/{}'.format(main_dir, urls_file_name)

    files_count = 0

    # TODO: Estructuras de prueba
    files = dict()
    files_terms = list()

    try:
        with get_file(urls_file_path) as urls_file:
            for ind, line in enumerate(urls_file):
                # \ufeff is a the ZERO WIDTH NO-BREAK SPACE codepoint.
                # It is used as a byte order mark in UTF-16 and UTF-32 to record the order in which the encoded bytes
                # are to be decoded (big-endian or little-endian).
                # UTF-8 doesn't need a BOM.
                # Para evitar errores, se remueve el caracter de la hilera
                line = line.replace('\ufeff', '')

                # Al separar las líneas por espacios en blanco, el primer elemento de la tupla corresponde
                # al nombre del archivo en la colección
                line_elems = line.split(' ')
                html_file_name = line_elems[0]
                html_url = line_elems[1]

                html_file_path = '{}/{}/{}'.format(main_dir, html_files_dir, html_file_name)

                with get_file(html_file_path) as html_file:
                    html_str = read_html_file(html_file, html_file_path)

                    # Procesamiento de la hilera leída del archivo html
                    text = process_html_str(html_str)

                    # TODO: Almacenar el resultado del procesamiento en las estructuras finales
                    # Para simular que se almacenan los resultados del procesamiento,
                    # se pone en la estructura files una entrada que tiene como key el nombre del archivo
                    # y como valor un k.
                    # En la estructura files_terms se pone la hilera del archivo como k-ésimo elemento.
                    files[html_file_name] = ind
                    files_terms.append(text)

                    files_count += 1

        # No es necesario llamar close sobre los archivos porque el contexto en el que está definido cada archivo
        # se encarga de cerrarlo

        print(files_count)
    except Exception as e:
        print('Excepción tipo {}:\t{}'.format(type(e), e))


def test():
    define_unicode_allowed_chars()

    url_path = '../RI_Coleccion/Coleccion/covid1.html'
    f = open(url_path)

    s = f.read()
    print('Longitud de la hilera normal: {}'.format(len(s)))

    s_texto = get_text_from_html_str(s)

    print('Longitud de la hilera solo texto: {}'.format(len(s_texto)))

    print('Texto: {}'.format(s_texto))

    # Remueve los caracteres de puntuación
    # Por el momento esto incluye eliminar todos los guiones
    s_texto = ' '.join(re.findall(r'\w+', s_texto, flags=re.UNICODE))
    tokens = nltk.word_tokenize(s_texto)

    print('Tokens: {}'.format(tokens))

    print()

    terms = list()
    print('EXCLUDED:')
    for token in tokens:
        if include_term(token.lower()):
            terms.append(token.lower())
        else:
            # Se imprimen primero los términos que se excluyen
            print(token)

    print()
    print('INCLUDED:')
    # Se imprime la lista de términos que se incluyen
    print(terms)


def run():
    main_dir = '../RI_Coleccion'
    urls_file_name = 'URLS.txt'
    html_files_dir = 'Coleccion'
    process_urls_files(main_dir, urls_file_name, html_files_dir)


def main():
    run()

    # Para probar funciones de procesamiento de texto
    # test()

    # Para medir tiempo de ejecución
    # begin_time = datetime.datetime.now()
    # run()
    # print(datetime.datetime.now() - begin_time)


if __name__ == '__main__':
    main()
