# utils/uploader.py
import io
import os
from uuid import uuid4


class Uploader:
    def __init__(self, base_dir: str = "./upload", base_url: str = "/static"):
        self.base_dir = base_dir
        self.base_url = base_url
        os.makedirs(self.base_dir, exist_ok=True)

    def upload_image(self, image, object_name: str, format: str = "png") -> str:
        """
        将图片字节数据写入本地 upload 目录，并返回可访问的静态 URL。
        """
        # 转为字节数据
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=format)
        image_bytes.seek(0)

        # 准备目录
        save_path = os.path.join(self.base_dir, object_name)
        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)

        # 写入本地文件
        with open(save_path, "wb") as f:
            f.write(image_bytes.read())

        return f"{self.base_url}/{object_name}"

    def upload_file(self, filepath: str, object_name: str) -> str:
        """
        将已有文件拷贝到 upload 目录，并返回可访问的静态 URL。
        """
        from shutil import copyfile

        dest_path = os.path.join(self.base_dir, object_name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        copyfile(filepath, dest_path)

        return f"{self.base_url}/{object_name}"
