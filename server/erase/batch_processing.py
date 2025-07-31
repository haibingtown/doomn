import json
from pathlib import Path
from typing import Dict, Optional

import torch
from PIL import Image
from iopaint.model_manager import ModelManager

def glob_images(path: Path) -> Dict[str, Path]:
    # png/jpg/jpeg
    if path.is_file():
        return {path.stem: path}
    elif path.is_dir():
        res = {}
        for it in path.glob("*.*"):
            if it.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                res[it.stem] = it
        return res


default_device = "cuda" if torch.cuda.is_available() else "cpu"
default_model = 'lama'
default_model_manager = ModelManager(name=default_model, device=default_device)


def batch_inpaint(
        image: Image,
        masks: [Image],
        model: Optional[str] = default_model,
        device: Optional[str] = default_model,
        config: Optional[Path] = None,
        concat: bool = False,
):
    return _batch_inpaint(image, masks, model, device, config, concat, default_model_manager)


def _batch_inpaint(
        image: Image,
        masks: [Image],
        model: Optional[str] = default_model,
        device: Optional[str] = default_model,
        config: Optional[Path] = None,
        concat: bool = False,
        model_manager: ModelManager = None,
):
    import cv2
    import numpy as np
    from iopaint.model.utils import torch_gc
    from iopaint.schema import InpaintRequest
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TimeElapsedColumn,
        MofNCompleteColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
    )

    if config is None:
        inpaint_request = InpaintRequest()
        inpaint_request.cv2_radius = 5
        inpaint_request.hd_strategy_crop_trigger_size = 640
        inpaint_request.hd_strategy_resize_limit = 2048
        inpaint_request.ldm_sampler = "ddim"
    else:
        with open(config, "r", encoding="utf-8") as f:
            inpaint_request = InpaintRequest(**json.load(f))

    if not model_manager:
        model_manager = ModelManager(name=model, device=device)

    console = Console()
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False,
    ) as progress:
        task = progress.add_task("Batch processing...", total=len(masks))

        img_np = np.array(image)
        img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        for mask in masks:

            mask_np = np.array(mask)
            # 检查掩码是否已经是单通道灰度图像
            if len(mask_np.shape) == 3:
                # 如果掩码是多通道的（如 RGB），则转换为灰度图像
                img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            else:
                # 否则，假设掩码已经是灰度图像
                mask_img = mask_np

            if mask_img.shape[:2] != img.shape[:2]:
                mask_img = cv2.resize(
                    mask_img,
                    (img.shape[1], img.shape[0]),
                    interpolation=cv2.INTER_NEAREST,
                )
            mask_img[mask_img >= 127] = 255
            mask_img[mask_img < 127] = 0

            # bgr
            inpaint_result = model_manager(img, mask_img, inpaint_request)
            img = cv2.cvtColor(inpaint_result, cv2.COLOR_BGR2RGB)
            if concat:
                mask_img = cv2.cvtColor(mask_img, cv2.COLOR_GRAY2RGB)
                img = cv2.hconcat([img, mask_img, inpaint_result])

            progress.update(task, advance=1)
            torch_gc()

    return Image.fromarray(inpaint_result)
