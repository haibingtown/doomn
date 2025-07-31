from server.base import Language
from server.providers.zh import ProviderZH


# @provider_register
class ProviderZH_JP(ProviderZH):
    
    def __init__(self):
        super().__init__(Language.JAPANESE)


    # def box_font(self):
    #     return Font.夏蝉圆体;