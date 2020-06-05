from ri_system.system import System


def main():
    ri_system = System(False)

    ri_system.prepare_collection()
    ri_system.index_collection()


if __name__ == '__main__':
    main()
