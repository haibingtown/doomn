import asyncio
import math
import time
from io import BytesIO
from typing import List, Type

import numpy as np
import requests
from PIL import Image, ImageFont, ImageDraw
from psd2fabric.fabric import Fabric
from psd2fabric.fabric.group import GroupFabricLayer
from psd2fabric.fabric.image import ImageFabricLayer
from psd2fabric.fabric.text import TextFabricLayer

from server.base import PicTransOcrBox, PicTransImage, Language, Font
from server.fabric.font_color import calculate_text_color
from server.ocr.base import OCR
from server.text.filter import is_number, is_weight, is_currency
from server.translate.base import Translate
from server.common.image_utils import crop_with_mask, is_solid_color, cal_threshold_using_kmeans, binarize_image, \
    adjust_vertices, points_to_rect, split_masks, dilated_mask
from server.common.utils import add_prefix_to_filename


def provider_register(cls):
    PROVIDERS.append(cls)
    return cls


def get_key(from_lan, to_lan):
    return f"{from_lan}-{to_lan}"


def crop_boxes(origin_image, ocr_boxes, box_padding):
    for bbox in ocr_boxes:
        # 取原始位置图像，计算二值化阈值
        rect = points_to_rect(origin_image, bbox.ocr_box, 0)
        rect_img = origin_image.crop(rect)
        th = cal_threshold_using_kmeans(rect_img)
        # 根据二值化图像自动调整 ocr_box的精度
        binary_img = binarize_image(origin_image, th)
        bbox.ocr_box = adjust_vertices(binary_img, bbox.ocr_box)
        # bbox.ocr_box = expanded_points(bbox.ocr_box, 2)

        # 正常流程
        bbox.box_img, bbox.text_mask, bbox.box_rect = crop_with_mask(origin_image, bbox.ocr_box, box_padding)
        bbox.box_solid, bbox.erase_img, _ = is_solid_color(bbox.box_img)


def mask_compose(origin_image, ocr_boxes):
    mask = Image.new('L', (origin_image.width, origin_image.height), color=0)
    # 将主 mask 也转换为 NumPy 数组
    mask_array = np.array(mask)
    for item in ocr_boxes:
        # 获取 box_rect 坐标
        left, top, right, bottom = item.box_rect
        # 将 text_mask 转换为 NumPy 数组
        text_mask_array = np.array(item.text_mask)
        # 将 text_mask 大于 0 的区域更新到主 mask 中
        mask_array[top:bottom, left:right] = np.where(text_mask_array > 0, text_mask_array,
                                                      mask_array[top:bottom, left:right])

    return Image.fromarray(mask_array)


def erase_togather(pt, ocr_boxes, padding=1):
    """
    合并所有mask, 再切成不连通的mask擦除，然后
    """
    mask = mask_compose(pt.origin_image, ocr_boxes)
    mask = dilated_mask(mask, 2)

    # 方案一：整体擦除
    # new_image = batch_inpaint(origin_image.convert("RGB"), [mask])

    # 方案二：拆解成独立的mask擦除
    origin_image = pt.origin_image
    new_image = origin_image.copy()
    masks = split_masks(mask)
    from .erase.batch_processing import batch_inpaint
    for m in masks:
        origin_image.putalpha(m)
        b = origin_image.getbbox()
        box = (
            min(b[0], b[0] - padding),
            min(b[1], b[1] - padding),
            max(b[2], b[2] + padding),
            max(b[3], b[3] + padding)
        )
        box_img = origin_image.crop(box)
        erase_img = batch_inpaint(box_img.convert("RGB"), [box_img.split()[3]])
        # box.erase_img.show()
        new_image.paste(erase_img, box)

    # 补一次，使得边缘平滑
    mask = dilated_mask(mask, 4)
    new_image = batch_inpaint(new_image.convert("RGB"), [mask])

    # 从擦图结果中截取背景
    new_image.putalpha(mask)
    for item in ocr_boxes:
        item.erase_img = new_image.crop(item.box_rect)
    return new_image.convert("RGB"), mask


def erase(pt, ocr_boxes, single=False, padding=10):
    """
    single: 是mask独立擦除，还是整体一起擦除

    *** 假定ocr的文字不会超出边框

    """
    if len(ocr_boxes) == 0:
        return

    # 过滤纯色背景、精调box的位置、生成text的mask
    crop_boxes(pt.origin_image, ocr_boxes, padding)
    un_solid = [item for item in ocr_boxes if not item.box_solid]
    # 根据mask擦除
    from .erase.batch_processing import batch_inpaint
    if single:
        # todo 重叠的mask进行合并擦除
        for box in un_solid:
            box.erase_img = batch_inpaint(box.box_img, [box.text_mask])
    else:
        erase_togather(pt, un_solid)


class PicTransProvider:
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
        erase(pt, pt.ocr_boxes)
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
        bg_layer = ImageFabricLayer("bg", 0, 0, pt.origin_image.width, pt.origin_image.height, pt.origin_image_url)
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

            t_layer.top = 0
            t_layer.left = 0
            t_layer.originX = 'center'
            t_layer.originY = 'center'

            group.add([b_layer, t_layer])
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
        bg_url = pt.context.task_context.oss_client.upload_image(box.erase_img, add_prefix_to_filename(pt.origin_image_name, f"_bg{index}"))
        b_layer = ImageFabricLayer(f"bg{index}", box.box_rect[0], box.box_rect[1], box.box_rect[2] - box.box_rect[0],
                                   box.box_rect[3] - box.box_rect[1],
                                   bg_url)
        b_layer.__setattr__("crossOrigin", "anonymous")
        b_layer.__setattr__("selectable", "false")

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


PROVIDERS: List[Type[PicTransProvider]] = []
