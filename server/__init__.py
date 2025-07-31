import json
import os
from abc import ABC
from typing import Dict
from urllib.parse import unquote

from psd2fabric.render.json_render import render_json

from fabric_render.fabric_render.py_bridge import fabric_img
from server import const
from server.base import PicTransImage, Font, Language, Context, PContext
from server.common.utils import change_ext_to_filename, add_prefix_to_filename
from server.engine import PicTransProvider, PROVIDERS, get_key, provider_register
from server.ocr.paddle_ocr import PaddleOcr
from server.providers.en.en_cht import ProviderEN_CHT
from server.providers.en.en_de import ProviderEN_DE
from server.providers.en.en_fra import ProviderEN_FRA
from server.providers.en.en_jp import ProviderEN_JP
from server.providers.en.en_kor import ProviderEN_KOR
from server.providers.en.en_th import ProviderEN_TH
from server.providers.en.en_vie import ProviderEN_VIE
from server.providers.en.en_zh import ProviderEN_ZH
from server.providers.zh.zh_cht import ProviderZH_CHT
from server.providers.zh.zh_de import ProviderZH_DE
from server.providers.zh.zh_en import ProviderZH_EN
from server.providers.zh.zh_fra import ProviderZH_FRA
from server.providers.zh.zh_jp import ProviderZH_JP
from server.providers.zh.zh_kor import ProviderZH_KOR
from server.providers.zh.zh_th import ProviderZH_TH
from server.providers.zh.zh_vie import ProviderZH_VIE
from server.translate.baidu import BaiduTranslator

provider_register(ProviderZH_JP)
provider_register(ProviderZH_EN)
provider_register(ProviderZH_CHT)
provider_register(ProviderZH_DE)
provider_register(ProviderZH_FRA)
provider_register(ProviderZH_KOR)
provider_register(ProviderZH_TH)
provider_register(ProviderZH_VIE)

provider_register(ProviderEN_JP)
provider_register(ProviderEN_ZH)
provider_register(ProviderEN_CHT)
provider_register(ProviderEN_DE)
provider_register(ProviderEN_FRA)
provider_register(ProviderEN_KOR)
provider_register(ProviderEN_TH)
provider_register(ProviderEN_VIE)


class PicTransTask(ABC):
    """
    payload
    {
        "to_lan": "jp",
        "from_lan": "cn",
        "image_url": "https://static-cse.canva.cn/blob/251287/YRinicGj15.bb913fe0.jpg"
    }

    return
    {
        "image_url": "https://static-cse.canva",
        "json_url": "https://static-cse"
    }
    """

    def __init__(self):
        super().__init__()
        self.engine = {}
        default_translator = BaiduTranslator()
        default_ocr_tool = PaddleOcr([
            Language.CHINESE, Language.ENGLISH, Language.Korean, Language.JAPANESE,
            Language.CHINESE_Traditional
        ])

        for p_cls in PROVIDERS:
            provider = p_cls()
            provider.set_translator(default_translator)
            provider.set_ocr_tool(default_ocr_tool)
            self.engine[provider.get_key()] = provider

    def run(self, task_ctx: Context, task_input: Dict) -> json:

        context = PContext(f"{const.UPLOADS_DIR}/{task_ctx.task_uid}", task_ctx, task_ctx.task_uid, task_input)

        from_lan = task_input['from_lan']
        to_lan = task_input['to_lan']
        url = task_input['image_url']
        url = unquote(url)

        p_key = get_key(from_lan, to_lan)
        if p_key not in self.engine:
            raise Exception(f'do not implement translate from {from_lan} to {to_lan}')

        provider = self.engine[p_key]
        pic_trans_image = PicTransImage(from_lan, to_lan, url, context)
        fabric = provider.trans(pic_trans_image)

        fabric_json = render_json(fabric)
        fabric_json = json.loads(fabric_json)

        # json_file_name = change_ext_to_filename(pic_trans_image.origin_image_name, '.json')
        # json_file = os.path.join(context.resource_dir, json_file_name)
        # with open(json_file, 'w') as jfile:
        #     json.dump(fabric_json, jfile, indent=4)
        #
        # img_file_name = add_prefix_to_filename(pic_trans_image.origin_image_name, "_pic_trans")
        # img_file = os.path.join(context.resource_dir, img_file_name)

        # font = provider.box_font()
        # fabric_img(json_file, img_file, fabric.clipPath["width"], fabric.clipPath["height"], [font.name], [font.value])

        # json_file_url = context.task_context.oss_client.upload_file(json_file, json_file_name)
        # img_file_trans = context.task_context.oss_client.upload_file(img_file, img_file_name)

        return {
            # "preview": img_file_trans,
            "content": fabric_json,
        }
