import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(_current_dir, '../'))
UPLOADS_DIR = os.path.join(ROOT_DIR, "uploads")
MODEL_DIR = os.path.join(ROOT_DIR, "models")