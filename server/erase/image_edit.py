import base64
import time
import json

import requests
from volcengine.visual.VisualService import VisualService

AK = "xxxx"
SK = "xxxx"
req_key = "seededit_v3.0"
visual = VisualService()
visual.set_ak(AK)
visual.set_sk(SK)


def image_to_base64(image_path_or_url):
    """
    支持本地文件路径或网络图片 URL 的转 base64 功能
    """
    try:
        if image_path_or_url.startswith("http://") or image_path_or_url.startswith("https://"):
            # 来自网络 URL
            resp = requests.get(image_path_or_url, timeout=10)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode("utf-8")
        else:
            # 来自本地路径
            with open(image_path_or_url, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to convert to base64: {e}")
        return None


def download_image(url, save_path):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return True
        else:
            print(f"❌ Failed to download image: {url}, status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception while downloading image: {e}")
        return False


def edit_image(url, query_max_retry=20, query_interval=3):
    # image url 直接传，被火山拦截概率高
    base64_str = image_to_base64(url)
    submit_req = {
        "req_key": req_key,
        "prompt": "删除文字",
        "binary_data_base64": [base64_str],
        "return_url": True
    }

    # task_id = "5107138009207428747"
    task_id = None
    if not task_id:
        try:
            submit_resp = visual.cv_sync2async_submit_task(submit_req)
        except Exception as e:
            return None, "", f"submit failed: {e}"

        try:
            task_id = submit_resp["data"]["task_id"]
        except (KeyError, TypeError):
            return None, "", "missing task_id in submit response"

    print(f" task_id => {task_id}")

    # Step 2: Polling task status
    for _ in range(query_max_retry):
        try:
            query_req = {
                "req_key": req_key,
                "task_id": task_id,
                "req_json": json.dumps({"return_url": True})
            }

            query_resp = visual.cv_sync2async_get_result(query_req)
            data = query_resp["data"]
            status_str = data.get("status")

            if status_str == "failed":
                return None, task_id, "task failed"
            if status_str == "done":
                return data["image_urls"][0], task_id, None

            time.sleep(query_interval)

        except Exception as e:
            return None, task_id, f"query failed: {e}"

    return None, task_id, f"task timeout after {query_max_retry} retries"
