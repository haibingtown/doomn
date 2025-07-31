from server.base import Language, PicTransOcrBox
from server.providers.en import ProviderEN


# @provider_register
class ProviderEN_DE(ProviderEN):

    def __init__(self):
        super().__init__(Language.German)

    def box_angle(self, box: PicTransOcrBox):
        """竖排时旋转90度"""
        return 90 if self.box_is_ver(box) else 0

    def box_text_content(self, box: PicTransOcrBox):
        return box.to_text
