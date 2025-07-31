import abc

from server.base import Language


class Translate(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def translate(self, from_lang: Language, to_lang: Language, queries):
        pass
