class DocumentEntry:
    def __init__(self, alias, html_str, url):
        self.__alias = alias
        self.__html_str = html_str
        self.__url = url
        self.__terms_dict = None

    def get_alias(self):
        return self.__alias

    def get_html_str(self):
        return self.__html_str

    def get_html_str(self):
        return self.__html_str

    def get_terms_dict(self):
        return self.__terms_dict

    def set_terms_dict(self, terms_dict):
        self.__terms_dict = terms_dict

