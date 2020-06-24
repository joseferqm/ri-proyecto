class SearchEngine:
    def __init__(self, collection_handler):
        self.__collection_handler = collection_handler

    def test_cuarta_etapa_search_engine(self):
        print('TEST 4TA ETAPA')
        # Cuando el sistema inicia con la colección procesada y llega una consulta
        # Se procesa la consulta utilizando la función del indexador
        query_terms = ["árbol", "pollo", "arbollll", "polloooo", "gato"]

        # Se buscan los términos de la consulta en el vocabulario
        # Filtered query terms debe estar ordenado alfabéticamente
        # para el orden de los vectores
        vocabulary = self.__collection_handler.get_vocabulary_entries()
        filtered_query_terms = [term for term in query_terms if term in vocabulary.keys()]

        print(query_terms)
        print(filtered_query_terms)

        documents = self.__collection_handler.get_documents_vectors_from_postings(filtered_query_terms)
        print(documents)
        # postings_result_docs = list()

        # Se calcula la similaridad del peso de cada documento de la lista de posteo con el peso de la consulta

        # postings_result_docs_wegiths = list()

        # Se hace el ranking respectivo para ordenar los documentos
        # Los documentos se identifican por ID en la lista de document_entries,
        # y lo que se devuelve es el document entry de cada uno
