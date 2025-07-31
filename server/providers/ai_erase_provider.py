import math
import time
from io import BytesIO
from typing import List

import numpy as np
import requests
from PIL import Image, ImageFont, ImageDraw
from psd2fabric.fabric import Fabric
from psd2fabric.fabric.group import GroupFabricLayer
from psd2fabric.fabric.image import ImageFabricLayer
from psd2fabric.fabric.text import TextFabricLayer

from server import Language, PicTransImage, add_prefix_to_filename, get_key
from server.base import PicTransOcrBox, Font
from server.engine import crop_boxes
from server.erase.image_edit import edit_image
from server.fabric.font_color import calculate_text_color
from server.ocr.base import OCR
from server.text.filter import is_number, is_weight, is_currency
from server.translate.base import Translate


class AiErasePicTransProvider:
    from_lan: Language
    to_lan: Language
    ocr_tool: OCR
    translator: Translate

    def __init__(self, from_lan: Language, to_lan: Language):
        self.from_lan = from_lan
        self.to_lan = to_lan

    def set_translator(self, translator):
        self.translator = translator

    def set_ocr_tool(self, ocr_tool):
        self.ocr_tool = ocr_tool

    def text_process(self, ocr_boxes):
        result = []
        for box in ocr_boxes:
            if is_number(box.text):
                continue

            if is_weight(box.text):
                continue

            if is_currency(box.text):
                continue
            result.append(box)
        return result

    def post_translate(self, ocr_boxes) -> []:
        result = []
        for box in ocr_boxes:
            # 翻译前后无变化不处理
            if box.text == box.to_text:
                continue
            result.append(box)
        return result

    def get_key(self):
        return get_key(self.from_lan.trans, self.to_lan.trans)

    def trans(self, pt: PicTransImage) -> Fabric:
        """
        核心流程
        """
        # step1: 文字内容和位置提取
        self.ocr(pt)
        # step2: 文字内容翻译
        self.translate(pt)
        # step3: 擦图
        start_time = time.time()

        pt.origin_image_file
        image_url, task_id, err = edit_image(pt.origin_image_file)
        if image_url != "":
            response = requests.get(image_url)
            response.raise_for_status()  # 如果请求失败会抛出异常
            new_image = Image.open(BytesIO(response.content))
            if new_image.size != pt.origin_image.size:
                new_image = new_image.resize(pt.origin_image.size, resample=Image.BILINEAR)
            pt.erase_image = new_image
            pt.erase_image_url = pt.context.task_context.oss_client.upload_image(pt.erase_image, add_prefix_to_filename(pt.origin_image_name, f"_bg"))

            crop_boxes(pt.origin_image, pt.ocr_boxes, 10)
            for item in pt.ocr_boxes:
                item.origin_img = pt.origin_image.crop(item.box_rect)
        else:
            raise Exception(err)

        print(f"Execution time: {time.time() - start_time} seconds")
        # step4: 合成
        return self.compose(pt)

    def ocr(self, pt: PicTransImage) -> List[PicTransOcrBox]:
        ocr_boxes = self.ocr_tool.ocr(np.array(pt.origin_image), pt.from_lan)
        # 过滤不需要处理的部分
        pt.ocr_boxes = self.text_process(ocr_boxes or [])

    def translate(self, pt: PicTransImage):
        from_texts = [box.text for box in pt.ocr_boxes]
        if len(from_texts) <= 0:
            return []

        texts = self.translator.translate(pt.from_lan, pt.to_lan, from_texts)

        for i, to_text in enumerate(texts):
            pt.ocr_boxes[i].to_lan = pt.to_lan
            pt.ocr_boxes[i].to_text = to_text

        # 翻译后处理,过滤掉无需翻译的内容
        pt.ocr_boxes = self.post_translate(pt.ocr_boxes)

    def compose(self, pt: PicTransImage) -> Fabric:
        """
        原图放在最底层
        每一个orc_box转化成2层，bg + text
        bg: 擦除后的背景
        text: 翻译后的文字
        """
        layers = []
        bg_layer = ImageFabricLayer("bg", 0, 0, pt.origin_image.width, pt.origin_image.height, pt.erase_image_url)
        bg_layer.__setattr__("crossOrigin", "anonymous")
        bg_layer.__setattr__("hasControls", False)
        bg_layer.__setattr__("selectable", False)
        bg_layer.__setattr__("lockMovementX", True)
        bg_layer.__setattr__("lockMovementY", True)
        layers.append(bg_layer)

        text_layers = []
        text_bg_layers = []

        for index, box in enumerate(pt.ocr_boxes):
            t_layer, b_layer = self.fabric_box(pt, index, box)

            group = GroupFabricLayer("翻译图层", b_layer.left, b_layer.top, b_layer.width, b_layer.height)

            b_layer.top = 0
            b_layer.left = 0
            b_layer.originX = 'center'
            b_layer.originY = 'center'
            b_layer.visible = False

            t_layer.top = 0
            t_layer.left = 0
            t_layer.originX = 'center'
            t_layer.originY = 'center'

            group.add([t_layer])
            group.type = 'd-pt-text'
            group.hasControls = False
            # group.selectable = False
            group.lockMovementX = True
            group.lockMovementY = True

            layers.append(group)

        layers.extend(text_bg_layers)
        layers.extend(text_layers)
        fb = Fabric(layers, 0, 0, pt.origin_image.width, pt.origin_image.height)
        fb.objects[0]['fill'] = "#ffffff"
        fb.background = "#ddd"
        return fb

    def fabric_box(self, pt: PicTransImage, index: int, box: PicTransOcrBox):
        # 1.文字的背景图层
        origin_url = pt.context.task_context.oss_client.upload_image(box.origin_img,
                                                                 add_prefix_to_filename(pt.origin_image_name,
                                                                                        f"_bg{index}"))
        b_layer = ImageFabricLayer(f"bg{index}", box.box_rect[0], box.box_rect[1], box.box_rect[2] - box.box_rect[0],
                                   box.box_rect[3] - box.box_rect[1],
                                   origin_url)
        b_layer.__setattr__("crossOrigin", "anonymous")
        b_layer.__setattr__("selectable", "false")
        b_layer.__setattr__("visible", "false")

        # 2. 字体层
        # 计算字体排列方向
        line = self.box_text_content(box)
        # 计算角度
        angle = self.box_angle(box)
        # 计算颜色
        font_color = self.box_font_color(box)
        # 字体
        font = self.box_font()
        # 计算文字的位置
        pos, size = self.box_font_pos_size(pt.origin_image, box, line, font, direction=self.box_direction(box))

        t_layer = TextFabricLayer(line, pos[0], pos[1], pos[2], pos[3])
        t_layer.set_text(font.name, size, line)
        t_layer.__setattr__("fill", f"rgb{font_color}")
        t_layer.__setattr__("angle", angle)
        t_layer.__setattr__("extra", {
            "from_lan": box.from_lan.trans,
            "to_lan": box.to_lan.trans,
            "from_text": box.text,
            "to_text": box.to_text
        })

        return t_layer, b_layer

    def box_is_ver(self, box: PicTransOcrBox):
        """
        是否竖排
        """
        return box.rect_width() < box.rect_height()

    def box_angle(self, box: PicTransOcrBox):
        # 计算两个点之间的差值
        x1, y1 = box.ocr_box[0]
        x2, y2 = box.ocr_box[1]

        delta_y = y2 - y1
        delta_x = x2 - x1

        # 使用 atan2 计算倾斜角度（以弧度为单位）
        angle_radians = math.atan2(delta_y, delta_x)

        # 将弧度转换为度数
        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    def box_font(self):
        return Font.AlibabaPuHuiTi

    def box_direction(self, box: PicTransOcrBox):
        """
        direction: Direction of the text. It can be 'rtl' (right to
                          left), 'ltr' (left to right) or 'ttb' (top to bottom).
                          Requires libraqm.
        """
        return 'rtl' if not self.box_angle(box) == 90 else 'ttb'

    def box_text_content(self, box: PicTransOcrBox):
        """竖排文字用换行符"""
        return box.to_text if not self.box_is_ver(box) else "\n".join(list(box.to_text.replace("\n", "")))

    def box_font_color(self, box: PicTransOcrBox):
        return calculate_text_color(box.erase_img)

    def get_font_size(self, draw, text, font, direction):
        text_bbox = draw.textbbox((0, 0), text, font=font, direction=direction)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return text_width, text_height

    def calculate_font_size(self, draw, text, rect_width, rect_height, font_path, direction='rtl'):
        """
        计算适应矩形的字体大小
        """
        max_font_size = 100
        # 最小 size = 8，再小就看不见了
        font_size = 8

        while True:
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = self.get_font_size(draw, text, font=font, direction=direction)
            if text_width > rect_width or text_height > rect_height or font_size > max_font_size:
                break

            font_size += 1

        return font_size - 1

    def box_font_pos_size(self, bg: Image, box: PicTransOcrBox, content, font, direction):
        draw = ImageDraw.Draw(bg)
        font_size = self.calculate_font_size(draw, content, box.rect_width(), box.rect_height(), font.value,
                                             direction=direction)
        text_width, text_height = self.get_font_size(draw, content, font=ImageFont.truetype(font.value, font_size),
                                                     direction=direction)

        # 居中
        start_position = (box.ocr_box[0][0] - (text_width - box.rect_width()) // 2,
                          box.ocr_box[0][1] - (text_height - box.rect_height()) // 2)
        return (start_position[0], start_position[1], text_width, text_height), font_size