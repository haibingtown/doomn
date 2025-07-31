from typing import List

from server.base import PicTransOcrBox, Language

DEFAULT_LAN = Language.CHINESE


class OCR(object):
    languages: [Language]

    def __init__(self, languages: [Language] = None):
        if languages is None:
            languages = Language.all_values()
        self.languages = languages

    def ocr(self, image, lan: Language, threshold=0.8) -> List[PicTransOcrBox]:
        pass
