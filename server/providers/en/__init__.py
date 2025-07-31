from server import PicTransProvider
from server.base import Language
from server.providers.ai_erase_provider import AiErasePicTransProvider


class ProviderEN(PicTransProvider):
    def __init__(self, to_lan: Language):
        super().__init__(Language.ENGLISH, to_lan)