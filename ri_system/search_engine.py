import numpy as np
from numpy import linalg as LA
from pyuca import Collator

from ri_system.analyzer import Analyzer
from ri_system.utilities import Utilities


class SearchEngine:
    def __init__(self, collection_handler):
        self.__collection_handler = collection_handler

    def test_cuarta_etapa_search_engine(self):
        print('TEST 4TA ETAPA')
        # Cuando el sistema inicia con la colección procesada y llega una consulta
        # Se procesa la consulta utilizando la función del indexador

        # Consulta de prueba 1
        query_string = "árbol pollo arbollll polloooo"
        # Consulta de prueba 2
        # query_string = "gato perro pollo arbollll polloooo"

        query_terms = Analyzer.retrieve_html_str_terms(query_string)
        # Se buscan los términos de la consulta en el vocabulario
        # Filtered query terms debe estar ordenado alfabéticamente para utilizar
        # dicho orden como orden de las entradas de los vectores
        collection_vocabulary = self.__collection_handler.get_vocabulary_entries()
        filtered_query_terms = [term for term in query_terms if term in collection_vocabulary.keys()]
        query_terms_np_array = np.array(filtered_query_terms)
        terms, counts = np.unique(query_terms_np_array, return_counts=True)
        query_vocabulary = dict(zip(terms, counts))
        max_l_freq_lq = max(counts)
        collator = Collator()
        final_query_terms = sorted(query_vocabulary.keys(), key=collator.sort_key)
        # Se obtiene el vector de pesos de la consulta
        query_weights_vector = SearchEngine.get_query_weights_vector(final_query_terms, max_l_freq_lq, query_vocabulary, collection_vocabulary)
        print(query_weights_vector)

        # Se recuperan las listas de posteo de cada palabra involucrada
        postings_lists = self.__collection_handler.get_postings_lists(final_query_terms)
        print(postings_lists)
        # Se obtienen los vectores de pesos para los documentos de las listas de posteo
        documents_weights_vectors = SearchEngine.get_documents_weights_short_vectors(postings_lists, final_query_terms)
        print(documents_weights_vectors)

        # Se calcula la similaridad del peso de cada documento de la lista de posteo con el peso de la consulta
        sorted_documents_aliases = sorted(documents_weights_vectors.keys(), key=collator.sort_key)
        query_documents_dot_products = SearchEngine.get_query_documents_dot_products(query_weights_vector, documents_weights_vectors, sorted_documents_aliases)
        print(query_documents_dot_products)
        query_documents_norms_products = self.get_query_documents_norms_products(query_weights_vector, sorted_documents_aliases)
        print(query_documents_norms_products)
        similarities = query_documents_dot_products / query_documents_norms_products
        print(similarities)

        for document_index, document_alias in enumerate(sorted_documents_aliases):
            print('{} -> {}'.format(document_alias, similarities[document_index]))

        # Se hace el ranking respectivo para ordenar los documentos
        # Los documentos se identifican por ID en la lista de document_entries,
        # y lo que se devuelve es el document entry de cada uno

    @staticmethod
    def get_query_weights_vector(terms, max_l_freq_lq, query_vocabulary, collection_vocabulary):
        query_vector = np.zeros(len(terms))
        for term_index, term in enumerate(terms):
            freq_iq = query_vocabulary[term]
            f_iq = freq_iq / max_l_freq_lq
            idf = collection_vocabulary[term]
            term_weight = Utilities.get_term_weight(f_iq, idf, True)
            query_vector[term_index] = term_weight

        return query_vector

    @staticmethod
    def get_documents_weights_short_vectors(postings_result, terms):
        documents_vectors = dict()
        for term_index, term in enumerate(terms):
            posting_list = postings_result[term]

            for posting_list_info_tuple in posting_list:
                document_alias = posting_list_info_tuple[0]
                term_weight = posting_list_info_tuple[1]
                if document_alias not in documents_vectors.keys():
                    documents_vectors[document_alias] = np.zeros(len(terms))
                documents_vectors[document_alias][term_index] = term_weight

        return documents_vectors

    @staticmethod
    def get_query_documents_dot_products(query_weights_vector, documents_weights_vectors, sorted_documents_aliases):
        documents_count = len(sorted_documents_aliases)
        dot_products = np.zeros(documents_count)

        for document_index, document_alias in enumerate(sorted_documents_aliases):
            document_weights_vector = documents_weights_vectors[document_alias]
            dot_product = np.dot(document_weights_vector, query_weights_vector)
            dot_products[document_index] = dot_product

        return dot_products

    def get_query_documents_norms_products(self, query_weights_vector, sorted_documents_aliases):
        documents_count = len(sorted_documents_aliases)
        norms_products = np.zeros(documents_count)
        query_vector_norm = LA.norm(query_weights_vector)
        documents_weights_vectors = self.__collection_handler.get_documents_weights_full_vectors(sorted_documents_aliases)
        for document_index, document_alias in enumerate(sorted_documents_aliases):
            document_vector_norm = LA.norm(documents_weights_vectors[document_index])
            norms_product = document_vector_norm * query_vector_norm
            norms_products[document_index] = norms_product

        return norms_products
