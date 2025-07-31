from server.base import Language
from server.providers.zh import ProviderZH


# @provider_register
class ProviderZH_KOR(ProviderZH):

    def __init__(self):
        super().__init__(Language.Korean)

