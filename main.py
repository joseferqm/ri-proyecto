from ri_system.system import System


def main():
    ri_system = System()

    ri_system.prepare_collection()
    ri_system.index_collection()

    # Para crear el archivo hyphenated_terms.txt
    # ri_system.prepare_collection()
    # ri_system.create_hyphenated_terms_file()

    # Para hacer pruebas con un documento específico
    # ri_system.index_document('covid1.html')
    # delitosinformaticos1.html

    # Para hacer pruebas con un documento aleatorio
    # ri_system.index_random_document()


if __name__ == '__main__':
    main()
