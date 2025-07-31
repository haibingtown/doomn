import io
import threading
import time
from functools import wraps
from typing import Callable
import time
import uuid

import oss2
import requests

# bucket: oss2.Bucket = None  # 延迟初始化
# last_update_time = 0

default_endpoint_url = "xxx"
default_bucket_name = "xxx"


class OSSClient:
    def __init__(self, get_sts: Callable[[], dict], bucket_name: str = default_bucket_name,
                 endpoint_url: str = default_endpoint_url,
                 update_interval: int = 600):
        """
        初始化 OSS 客户端
        :param get_sts: 获取 STS 凭证的函数，需返回包含 accessKeyId, accessKeySecret, securityToken, bucket 和 endpoint 的字典
        :param update_interval: STS 凭证更新间隔，默认 10 分钟
        """
        self.get_sts = get_sts
        self.update_interval = update_interval
        self.bucket: oss2 = None
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.last_update_time = 0
        self.lock = threading.Lock()  # 保证线程安全

    def update_oss_credentials(self):
        """更新 OSS 凭证"""
        with self.lock:  # 确保线程安全
            if time.time() - self.last_update_time > self.update_interval or self.bucket is None:
                token_response = self.get_sts()
                auth = oss2.StsAuth(
                    token_response["accessKeyId"],
                    token_response["accessKeySecret"],
                    token_response["securityToken"]
                )
                # self.bucket_name = token_response["bucket"]
                # self.endpoint_url = token_response["endpoint"]
                self.bucket = oss2.Bucket(auth, self.endpoint_url, self.bucket_name)
                self.last_update_time = time.time()

    def upload_image(self, image, object_name: str, format: str = 'png') -> str:
        """
        上传图像到 OSS
        :param image: PIL 图像对象
        :param object_name: 上传到 OSS 的对象名称
        :param format: 图像格式，默认 'png'
        :return: 上传后的文件访问 URL
        """
        self.update_oss_credentials()

        image_bytes = io.BytesIO()
        image.save(image_bytes, format=format)
        image_bytes.seek(0)
        self.bucket.put_object(object_name, image_bytes)
        return f'https://{self.bucket_name}.{self.endpoint_url.replace("https://", "")}/{object_name}'

    def upload_file(self, filepath: str, object_name: str) -> str:
        """
        上传文本内容到 OSS
        :param filepath: 文本内容
        :param object_name: 上传到 OSS 的对象名称
        :return: 上传后的文件访问 URL
        """
        self.update_oss_credentials()
        self.bucket.put_object_from_file(object_name, filepath)
        return f'https://{self.bucket_name}.{self.endpoint_url.replace("https://", "")}/{object_name}'

    def upload_remote_file(self, remote_url, object_name):
        """
        下载远程文件并上传到 OSS

        :param remote_url: 远程文件的 URL
        :param object_name: 远程对象名（在 OSS 中的路径，例如 'folder/file.jpg'）
        :return: 上传结果的 URL 或 None
        """
        self.update_oss_credentials()
        # 下载远程文件
        response = requests.get(remote_url, stream=True)
        response.raise_for_status()
        # 将文件内容读取到内存
        file_data = io.BytesIO(response.content)
        # 上传到 OSS
        self.bucket.put_object(object_name, file_data)
        return f'https://{self.bucket_name}.{self.endpoint_url.replace("https://", "")}/{object_name}'
