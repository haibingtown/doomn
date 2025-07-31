import os
import tempfile
from uuid import uuid4

import anyio
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from server import Context, PicTransTask
from server.const import UPLOADS_DIR
from server.files.uploader import Uploader

host='127.0.0.1'
port=8000
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 允许的源
    allow_credentials=True,           # 是否支持 cookies
    allow_methods=["*"],              # 允许的 HTTP 方法
    allow_headers=["*"],              # 允许的请求头
)
task_processor = PicTransTask()

os.makedirs(UPLOADS_DIR, exist_ok=True)
# 静态资源路由，用于访问上传的图片
app.mount("/static", StaticFiles(directory=UPLOADS_DIR), name="static")

uploader = Uploader(base_dir=UPLOADS_DIR, base_url=f'http://{host}:{port}/static')

# 请求体模型
class TranslateImageInput(BaseModel):
    to_lan: str
    from_lan: str
    image_url: str

@app.post("/upload_image")
async def upload_image(image: UploadFile = File(...)):
    try:
        ext = os.path.splitext(image.filename)[-1].lower().strip(".") or "png"
        object_name = f"images/{uuid4().hex}.{ext}"

        # 写入临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(await image.read())
            tmp_path = tmp.name

        # 上传并删除临时文件
        image_url = uploader.upload_file(tmp_path, object_name)
        os.remove(tmp_path)

        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/pic_trans")
async def translate_image(task_input: TranslateImageInput, request: Request):
    try:
        # 构造上下文
        ctx = Context(task_uid=f"{uuid4().hex}", task_type=f"pic_trans", oss_client=uploader)

        # 执行任务
        result = await anyio.to_thread.run_sync(task_processor.run, ctx, task_input.dict())

        # 确保是 JSON 可序列化的
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 入口函数：直接运行 FastAPI 服务
def main():
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
