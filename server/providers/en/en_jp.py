from server.base import Language
from server.providers.en import ProviderEN


# @provider_register
class ProviderEN_JP(ProviderEN):
    
    def __init__(self):
        super().__init__(Language.JAPANESE)


    # def box_font(self):
    #     return Font.夏蝉圆体;