from typing import List

from server.base import Language
from server.ocr.base import OCR, PicTransOcrBox


class PaddleOcr(OCR):
    from numpy import ndarray
    # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
    # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
    paddle_ocrs = {}

    def __init__(self, languages: [Language] = None):
        super().__init__(languages)

        for lan in self.languages:
            self.load(lan)

    def load(self, lan: Language):
        if lan.ocr not in self.paddle_ocrs.items():

            from paddleocr import PaddleOCR
            self.paddle_ocrs[lan.ocr] = PaddleOCR(use_angle_cls=True, lang=lan.ocr)

    def ocr(self, image: ndarray, lan: Language, threshold=0.85) -> List[PicTransOcrBox]:
        orc_boxes = []
        orc_tool = self.paddle_ocrs[lan.ocr]
        boxes = orc_tool.ocr(image, cls=True)
        for box in boxes[0]:
            if box[1][1] < threshold:
                continue

            orc_box = PicTransOcrBox(lan)
            orc_box.ocr_box = box[0]
            orc_box.text = box[1][0]
            orc_boxes.append(orc_box)
        return orc_boxes
