from ri_system.system import System


def main():
    ri_system = System(True)

    ri_system.prepare_collection()
    ri_system.index_collection()

    # Para hacer pruebas con un documento específico
    # ri_system.index_document('delitosinformaticos1.html')
    # delitosinformaticos1.html

    # Para hacer pruebas con un documento aleatorio
    # ri_system.index_random_document()


if __name__ == '__main__':
    main()
