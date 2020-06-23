import enum


class CollectionOutputFiles(enum.Enum):
    VOCABULARY = 1
    INDEX = 2
    POSTINGS = 3


class DocumentOutputFiles(enum.Enum):
    TOK = 1
    WTD = 2
