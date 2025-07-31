import os
import uuid
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from PIL import Image
from psd2fabric.fabric import Fabric

from server.common.utils import download_file
from server.files.uploader import Uploader

folder = os.path.dirname(os.path.abspath(__file__))


class Context:
    oss_client: Uploader = None
    task_uid: str
    task_type: str

    def __init__(self, task_uid: str, task_type: str, oss_client: Uploader):
        self.task_uid = task_uid
        self.task_type = task_type
        self.oss_client = oss_client


class PContext:
    """
    图片翻译的上线文
    """
    task_id: str
    resource_dir: str
    payload: Dict
    task_context: Context

    def __init__(self, resource_dir: str, task_context: Context, task_id: str = None, payload: Dict = None):
        self.resource_dir = resource_dir
        self.task_id = task_id
        self.payload = payload
        self.task_context = task_context

    def set_payload(self, payload: str):
        self.payload = payload


class Font(Enum):
    """
    默认字体
    """
    YouSheBiaoTiHei = f'{folder}/assets/font/YouSheBiaoTiHei.ttf'
    NatsuzemiMaruGothic = f'{folder}/assets/font/NatsuzemiMaruGothic-Black.ttf'
    # https://github.com/atelier-anchor/smiley-sans
    SmileySans = f'{folder}/assets/font/SmileySans-Oblique.ttf'
    AlibabaPuHuiTi = f'{folder}/assets/font/AlibabaPuHuiTi-3-55-Regular.ttf'


class Language(Enum):
    """
    trans: 翻译的语言定义
    ocr: ocr识别的语言定义
    """
    ENGLISH = ('en', 'en')
    CHINESE = ('zh', 'ch')
    JAPANESE = ('jp', 'japan')
    CHINESE_Traditional = ('cht', 'chinese_cht')  # 繁体
    Korean = ('kor', 'korean')  # 韩国

    """ 以下 orc 暂不支持 """
    Vietnamese = ('vie', 'vie')  # 越南
    German = ('de', 'german')  # 德国
    French = ('fra', 'fr')  # 法国
    Thai = ('th', 'th')  # 泰国

    Czech = ('cs', 'cs')  # 捷克
    Dutch = ('nl', 'nl')  # 荷兰
    Hungarian = ('hu', 'hu')  # 匈牙利
    Italian = ('it', 'it')  # 意大利
    Polish = ('pl', 'pl')  # 波兰
    Portuguese = ('pt', 'pt')  # 葡萄牙
    Romanian = ('rom', 'rom')  # 罗马尼亚
    Russian = ('ru', 'ru')  # 俄国
    Spanish = ('spa', 'spa')  # 西班牙
    Serbian = ('srp', 'srp')  # 塞尔维亚
    Croatian = ('hrv', 'hrv')  # 克罗地亚

    def __init__(self, trans, ocr):
        self.ocr = ocr
        self.trans = trans

    @classmethod
    def all_values(cls) -> List['Language']:
        return list(cls)

    @staticmethod
    def from_tran(tran_value: str) -> Optional['Language']:
        for lang in Language:
            if lang.trans == tran_value:
                return lang
        return None


class PicTransOcrBox:
    """
    识别的字体区域
    """

    from_lan: Language  # 原始语言
    to_lan: Language  # 目标语言
    ocr_box: []  # ocr识别的原始文字区域，顺时针的四个顶点，区域可能非严格矩形。eg: [(0,0),(1,0),(1,1),(0,1)]
    box_rect: Tuple[int, int, int, int]  # 背景的矩形bbox, eg:(left, top, width, height), 根据ocr_box转换
    box_padding: int  # box裁剪时增加边框距离
    box_img: Image  # 从原图上裁剪下来的图片
    box_solid: bool  # 背景是否是纯色
    text_mask: Image  # 裁剪图片的mask
    text: str  # 原始文本
    to_text: str  # 目标文本
    erase_img: Image  # 原图擦除后的背景图片
    origin_img: Image  # 原始图片

    def __init__(self, from_lan: Language) -> None:
        self.from_lan = from_lan

    def rect_width(self):
        return max(self.ocr_box[1][0] - self.ocr_box[0][0], self.ocr_box[2][0] - self.ocr_box[3][0])

    def rect_height(self):
        return max(self.ocr_box[2][1] - self.ocr_box[1][1], self.ocr_box[3][1] - self.ocr_box[0][1])


class PicTransImage:
    context: PContext
    from_lan: Language  # 原始语言
    to_lan: Language  # 目标语言
    origin_image: Image  # 原始图片
    origin_image_url: str  # 原始图片的url地址
    origin_image_file: str  # 图片本地链接
    origin_image_name: str  # 原始图片文件名称
    erase_image: Image  # 擦除后的图片
    erase_image_url: str  # 擦除后图片链接

    ocr_boxes: List[PicTransOcrBox]  # 提取的文字

    fabric: Fabric  # 渲染之后的fabric

    def __init__(self, from_lan: str, to_lan: str, image_url: str, context: PContext) -> None:
        self.from_lan = Language.from_tran(from_lan)
        self.to_lan = Language.from_tran(to_lan)
        if not self.from_lan or not self.to_lan:
            raise Exception(f"not implement for translate from {from_lan} to {to_lan}")

        self.context = context
        self.origin_image_url = image_url

        # 图片预处理
        # url_path = Path(image_url)
        self.origin_image_file = download_file(image_url, self.context.resource_dir)
        self.origin_image_name = Path(self.origin_image_file).name
        self.origin_image = Image.open(self.origin_image_file).convert('RGB')

        self.origin_image_url = context.task_context.oss_client.upload_image(self.origin_image,
                                                                             f'{uuid.uuid4().hex}.jpg')
