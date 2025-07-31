from server.base import Language
from server.providers.en import ProviderEN


# @provider_register
class ProviderEN_CHT(ProviderEN):

    def __init__(self):
        super().__init__(Language.CHINESE_Traditional)
