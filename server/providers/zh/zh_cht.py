from server.base import Language
from server.providers.zh import ProviderZH


# @provider_register
class ProviderZH_CHT(ProviderZH):

    def __init__(self):
        super().__init__(Language.CHINESE_Traditional)
