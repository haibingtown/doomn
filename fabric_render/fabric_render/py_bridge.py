import os
import subprocess
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
node_script = os.path.join(current_dir, 'fabric_render.js')


def call_node_script(output_file, json_file, width, height, font_families=None, font_paths=None):
    args = [
        'node',
        node_script,
        output_file,
        json_file,
        str(width),
        str(height),
        ','.join(font_families) if font_families else '',
        ','.join(font_paths) if font_paths else ''
    ]

    result = subprocess.run(args, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Success: {result.stdout}")

    return result.returncode


def fabric_img(json_file, output_file, width, height, font_families, font_paths):
    call_node_script(output_file, json_file, width, height, font_families, font_paths)