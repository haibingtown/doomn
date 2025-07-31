from server import PicTransProvider
from server.base import Language
from server.providers.ai_erase_provider import AiErasePicTransProvider


class ProviderZH(PicTransProvider):
    def __init__(self, to_lan: Language):
        super().__init__(Language.CHINESE, to_lan)
