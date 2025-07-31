#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import secrets
import shutil
import tempfile
from pathlib import Path

import requests
from PIL import JpegImagePlugin


def singleton(cls):
    _instances = {}

    def get_instance():
        if cls not in _instances:
            _instances[cls] = cls()
        return _instances[cls]

    return get_instance


def image_with_json(img, json):
    # 添加EXIF元数据
    exif = img.info.get('exif', b'')
    new_exif = JpegImagePlugin.get_default_exif()
    new_exif[37510] = json  # 使用37510（UserComment）标签存储JSON信息
    img.save("output_image_with_metadata.jpg", "jpeg", exif=new_exif)
    return img


def add_prefix_to_filename(filename, prefix):
    """
    在文件名的后缀名前添加前缀字符串。

    :param filename: 原始文件名
    :param prefix: 要添加的前缀字符串
    :return: 修改后的文件名
    """
    # 分离文件名和扩展名
    base, ext = os.path.splitext(filename)

    # 在扩展名前添加前缀
    new_filename = f"{base}{prefix}{ext}"

    return new_filename


def change_ext_to_filename(filename, ext):
    """
        在文件名的后缀名前添加前缀字符串。

        :param filename: 原始文件名
        :param prefix: 要添加的前缀字符串
        :return: 修改后的文件名
        """
    # 分离文件名和扩展名
    base, _ = os.path.splitext(filename)
    # 在扩展名前添加前缀
    new_filename = f"{base}{ext}"
    return new_filename


def get_filename_from_path(image_path):
    """
    从文件路径中提取文件名
    :param image_path: 文件路径
    :return: 文件名
    """
    return os.path.basename(image_path)


def download_file(url_path: str, save_dir: str) -> str:
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)

    temp_dir = Path(tempfile.gettempdir()) / secrets.token_hex(20)
    temp_dir.mkdir(exist_ok=True, parents=True)

    with requests.get(url_path) as response:
        response.raise_for_status()
        with open(temp_dir / Path(url_path).name, "wb") as f:
            f.write(response.content)

    directory = Path(save_dir)
    directory.mkdir(exist_ok=True, parents=True)
    dest = directory / Path(url_path).name
    shutil.move(temp_dir / Path(url_path).name, dest)
    return str(dest.resolve())
