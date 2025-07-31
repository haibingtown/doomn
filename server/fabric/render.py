from PIL import ImageFont

def get_font_size(draw, text, font, direction):
    text_bbox = draw.textbbox((0, 0), text, font=font, direction=direction)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    return text_width, text_height


def calculate_font_size(draw, text, rect_width, rect_height, font_path, direction='rtl'):
    """
    计算适应矩形的字体大小
    """
    max_font_size = 100
    font_size = 1

    while True:
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = get_font_size(draw, text, font=font, direction=direction)
        if text_width > rect_width or text_height > rect_height or font_size > max_font_size:
            break

        font_size += 1

    return font_size - 1

