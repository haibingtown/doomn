from server.base import Language
from server.providers.en import ProviderEN


# @provider_register
class ProviderEN_KOR(ProviderEN):

    def __init__(self):
        super().__init__(Language.Korean)

