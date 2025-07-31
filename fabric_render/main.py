from PIL import Image

from fabric_render.py_bridge import fabric_img


json_file = "/Users/haibing/dev/github/ppt/.tmp/auto/7781_template.json"
json_png = "/Users/haibing/dev/github/ppt/.tmp/auto/7781_template2.png"
fabric_img(json_file, json_png, 1080, 1080, None, None)
Image.open(json_png).show()