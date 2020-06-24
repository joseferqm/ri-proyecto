from ri_system.system import System


def main():
    ri_system = System(False)

    ri_system.prepare_collection()
    # ri_system.index_collection()

    ri_system.test_cuarta_etapa()


if __name__ == '__main__':
    main()
