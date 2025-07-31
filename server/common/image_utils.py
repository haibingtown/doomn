from collections import Counter

import cv2
import numpy as np
from PIL import ImageDraw, Image, ImageFilter
from scipy.ndimage import binary_dilation
from sklearn.cluster import KMeans


def expanded_points(points, padding):
    # 将矩形的四个顶点分别提取
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    x4, y4 = points[3]

    # 向外扩展size个像素
    ex_points = [
        (x1 - padding, y1 - padding),
        (x2 + padding, y2 - padding),
        (x3 + padding, y3 + padding),
        (x4 - padding, y4 + padding)
    ]
    return ex_points


def scale_points(points, factor):
    # 提取顶点坐标
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    x4, y4 = points[3]

    # 计算中心点
    cx = (x1 + x2 + x3 + x4) / 4
    cy = (y1 + y2 + y3 + y4) / 4

    # 计算新的顶点坐标
    new_points = []
    for x, y in points:
        new_x = cx + factor * (x - cx)
        new_y = cy + factor * (y - cy)
        new_points.append((new_x, new_y))

    return new_points


def crop_points(image, points, padding):
    # 根据边界框裁剪结果图像
    bbox = points_to_rect(image, points, padding)
    cropped_image = image.crop(bbox)
    return cropped_image, bbox


def points_to_rect(image, points, padding):
    ex_points = [(int(x), int(y)) for x, y in points]
    # ex_points = expanded_points(points, padding)
    # 计算四边形的边界框
    min_x = int(max(min(p[0] for p in ex_points) - padding, 0))
    min_y = int(max(min(p[1] for p in ex_points) - padding, 0))
    max_x = int(min(max(p[0] for p in ex_points) + padding, image.width))
    max_y = int(min(max(p[1] for p in ex_points) + padding, image.height))
    # 根据边界框裁剪结果图像
    rect = (min_x, min_y, max_x, max_y)
    return rect


def crop_with_mask(image: Image, coordinates, padding=6):
    """
    从图像中裁剪一个由四个顶点坐标定义的非矩形区域（不规则四边形），
    并向四周扩展指定的像素边距，同时返回一个相同大小的掩码。

    :param image: PIL 图像对象
    :param coordinates: 四个顶点坐标 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    :param padding: 向四周扩展的像素边距，默认是 10 像素。
    :return: (裁剪后的图像, 裁剪区域的掩码)
    """
    image = image.convert("RGB")
    # 创建一个与图像相同大小的黑色掩码图像
    mask = Image.new("L", image.size, 0)
    points = [(int(x), int(y)) for x, y in coordinates]
    ImageDraw.Draw(mask).polygon(points, outline=None, fill=255)
    image.putalpha(mask)

    # todo 竖排文字
    # padding = int((coordinates[3][1] - coordinates[0][1]) * 0.1)
    # if padding > 6:
    #     padding = 6

    # 根据边界框裁剪结果图像
    bbox = points_to_rect(image, points, padding)
    # mask，大小与裁剪区域相同
    cropped_image = image.crop(bbox)
    return cropped_image.convert("RGB"), cropped_image.split()[3], bbox


def text_filter(text):
    return text.isdigit()


def text_filter_logo(box, image):
    x = box[0][0]
    y = box[0][1]
    width = box[1][0] - box[0][0]
    height = box[2][1] - box[1][1]

    center_x = x + width // 2
    center_y = y + height // 2
    return ((center_x < (image.width // 5)) or
            ((image.width - center_x) < (image.width // 5))) \
        and (center_y < (image.height // 5))


def create_mask_pil(mask, points, padding=8, fill=255):
    # 创建Draw对象，用于绘制多边形
    draw = ImageDraw.Draw(mask)
    points = [(int(x), int(y)) for x, y in points]
    # 向外扩展size个像素
    points = expanded_points(points, padding)
    # 在mask上绘制多边形，填充为255
    draw.polygon(points, fill=fill)


def color_distance(c1, c2):
    """
    计算两个颜色之间的欧氏距离
    """
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5


def is_similar_color(c1, c2, tolerance=10):
    """
    判断两个颜色是否在容差范围内
    """
    return color_distance(c1, c2) <= tolerance


def is_solid_color(img, border=1, tolerance=0.8, color_tolerance=10):
    # 将图像转换为 RGB 模式
    img = img.convert('RGB')
    width, height = img.size
    # 获取最外围 2 个像素的矩形圈
    pixels = []
    # 上边框
    pixels += list(img.crop((0, 0, width, border)).getdata())
    # 下边框
    pixels += list(img.crop((0, height - border, width, height)).getdata())
    # 左边框
    pixels += list(img.crop((0, border, border, height - border)).getdata())
    # 右边框
    pixels += list(img.crop((width - border, border, width, height - border)).getdata())

    # 归类颜色
    color_groups = []
    for pixel in pixels:
        found_group = False
        for group in color_groups:
            if is_similar_color(group[0], pixel, color_tolerance):
                group.append(pixel)
                found_group = True
                break
        if not found_group:
            color_groups.append([pixel])

    # 找到最大的颜色组
    largest_group = max(color_groups, key=len)
    largest_group_color = largest_group[0]
    largest_group_ratio = len(largest_group) / len(pixels)

    if largest_group_ratio >= tolerance:
        # 将图像设置为纯色
        img = Image.new('RGB', (width, height), largest_group_color)
        return True, img, largest_group_color

    return False, img, None


def get_text_mask(img):
    # 1. 打开图像并转换为L格式
    image = img.convert("L")

    # 2. 去掉外围2个像素
    cropped_image = image.crop((2, 2, image.width - 2, image.height - 2))

    # 3. 找到图像中最大像素值
    # 3. 找到图像中数量最多的像素值
    pixel_counts = cropped_image.getcolors(cropped_image.width * cropped_image.height)
    most_common_pixel_value = max(pixel_counts, key=lambda x: x[0])[1]

    # 4. 计算上下各25的范围
    lower_bound = max(0, most_common_pixel_value - 25)
    upper_bound = min(255, most_common_pixel_value + 25)

    # 5. 创建一个新的透明图像
    mask = Image.new("L", image.size, 0)

    # 6. 将符合范围的像素设为不透明
    for x in range(cropped_image.width):
        for y in range(cropped_image.height):
            pixel_value = cropped_image.getpixel((x, y))
            if lower_bound <= pixel_value <= upper_bound:
                mask.putpixel((x + 2, y + 2), 255)  # 调整回原始图像位置

    mask = mask.filter(ImageFilter.MaxFilter(size=1))  # 使用5x5的MaxFilter来膨胀2像素

    return mask


def find_two_most_common_colors(gray_image):
    # 获取图像中的所有像素值
    pixels = list(gray_image.getdata())

    # 统计每种灰度值的出现次数
    counter = Counter(pixels)

    # 找到出现频率最高的两个灰度值
    most_common = counter.most_common(2)

    # 返回这两个灰度值
    return most_common[0][0], most_common[1][0]


def cal_threshold(image):
    image = image.convert('L')

    # 寻找最常见的两种灰度值
    color1, color2 = find_two_most_common_colors(image)

    # 计算这两种颜色的中间值
    return (color1 + color2) // 2


def binarize_image(image, threshold=127):
    image = image.convert('L')
    # 二值化图像
    binary_image = image.point(lambda p: 255 if p > threshold else 0)
    return binary_image


def cal_threshold_using_kmeans(image):
    # 将图像转换为灰度图并获取像素值
    gray_image = image.convert('L')
    pixels = np.array(gray_image).reshape(-1, 1)
    # 使用K-means聚类，将灰度值分为两类
    kmeans = KMeans(n_clusters=2, random_state=42)
    kmeans.fit(pixels)
    # 获取聚类中心
    centers = sorted(kmeans.cluster_centers_.flatten())
    # 计算两个聚类中心的中间值，作为阈值
    threshold = int((centers[0] + centers[1]) / 2)
    return threshold


def get_line_pixels(image, start, end):
    # 使用Bresenham算法获取两点之间的像素点
    x0, y0 = start
    x1, y1 = end
    pixels = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        pixels.append(image.getpixel((x0, y0)))
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return pixels


def point_in_border(image, point):
    if point[0] < 0 or point[0] >= image.width or point[1] < 0 or point[1] >= image.height:
        return False
    else:
        return True


def expand_and_check(image, start, end, d, max_expansion=12, min_expansion=4):
    if min_expansion > 0:
        if d == "top":
            start = (start[0], start[1] + min_expansion)
            end = (end[0], end[1] + min_expansion)
        elif d == "right":
            start = (start[0] - min_expansion, start[1])
            end = (end[0] - min_expansion, end[1])
        elif d == "bottom":
            start = (start[0], start[1] - min_expansion)
            end = (end[0], end[1] - min_expansion)
        elif d == "left":
            start = (start[0] + min_expansion, start[1])
            end = (end[0] + min_expansion, end[1])

    result = (start, end)
    for i in range(max_expansion):
        pixels = get_line_pixels(image, start, end)
        if len(set(pixels)) == 1:
            break

        if d == "top":
            start = (start[0], start[1] - 1)
            end = (end[0], end[1] - 1)
        elif d == "right":
            start = (start[0] + 1, start[1])
            end = (end[0] + 1, end[1])
        elif d == "bottom":
            start = (start[0], start[1] + 1)
            end = (end[0], end[1] + 1)
        elif d == "left":
            start = (start[0] - 1, start[1])
            end = (end[0] - 1, end[1])

        if not point_in_border(image, start) or not point_in_border(image, end):
            break

        result = (start, end)

    return result


def adjust_vertices(binary_image, points, max_expansion=12, min_expansion=4):
    # 提取四个顶点
    top_left, top_right, bottom_right, bottom_left = points

    # 检查并扩展四条边
    top_left, top_right = expand_and_check(binary_image, top_left, top_right, "top", max_expansion, min_expansion)
    top_right, bottom_right = expand_and_check(binary_image, top_right, bottom_right, "right", max_expansion,
                                               min_expansion)
    bottom_right, bottom_left = expand_and_check(binary_image, bottom_right, bottom_left, "bottom",
                                                 max_expansion, min_expansion)
    bottom_left, top_left = expand_and_check(binary_image, bottom_left, top_left, "left", max_expansion, min_expansion)

    # 返回调整后的顶点
    return top_left, top_right, bottom_right, bottom_left


def detect_possible_background_colors(image, edge_sample_size=10, n_clusters=3):
    pixels = np.array(image)

    # 提取图像边缘的像素点（上下左右边缘）
    edge_pixels = np.concatenate([
        pixels[:edge_sample_size, :, :3].reshape(-1, 3),  # 上边缘
        pixels[-edge_sample_size:, :, :3].reshape(-1, 3),  # 下边缘
        pixels[:, :edge_sample_size, :3].reshape(-1, 3),  # 左边缘
        pixels[:, -edge_sample_size:, :3].reshape(-1, 3)  # 右边缘
    ])

    # 使用KMeans聚类分析边缘颜色
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(edge_pixels)
    possible_background_colors = kmeans.cluster_centers_

    return [tuple(map(int, color)) for color in possible_background_colors]


def filter_background_and_extract_text_color(image, background_tolerance=30):
    pixels = np.array(image)

    pixels = pixels.reshape(-1, pixels.shape[-1])

    if pixels.shape[1] == 4:
        pixels = pixels[pixels[:, 3] != 0, :3]

    # 检测可能的背景色
    possible_background_colors = detect_possible_background_colors(image, edge_sample_size=2)

    # 过滤掉与可能背景色接近的颜色
    filtered_pixels = []
    for pixel in pixels:
        if not any(all(abs(pixel[i] - bg_color[i]) < background_tolerance for i in range(3))
                   for bg_color in possible_background_colors):
            filtered_pixels.append(tuple(pixel))

    # 如果过滤后没有剩余像素，返回默认颜色
    if not filtered_pixels:
        return possible_background_colors[0]  # 返回最常见的背景颜色

    color_counter = Counter(filtered_pixels)
    most_common_color = color_counter.most_common(1)[0][0]

    return most_common_color


def split_masks(mask: Image.Image):
    # 将 PIL Image 转换为 OpenCV 格式的灰度图像
    mask_cv = np.array(mask.convert('L'))  # 转换为灰度模式 ('L')

    # 将灰度图像二值化，前景区域为 255，背景区域为 0
    _, binary_mask = cv2.threshold(mask_cv, 1, 255, cv2.THRESH_BINARY)

    # 查找前景区域的轮廓
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 创建一个空列表来存储每个独立的掩码
    independent_masks = []

    # 遍历所有轮廓，提取每个轮廓对应的掩码
    for i, contour in enumerate(contours):
        # 创建一个与原始 mask 大小相同的空白掩码
        single_mask = np.zeros_like(binary_mask)

        # 将当前轮廓填充到单独的掩码上
        cv2.drawContours(single_mask, contours, i, color=255, thickness=-1)

        # 将 NumPy 数组转换回 PIL 图像
        pil_mask = Image.fromarray(single_mask)

        # 将这个独立的掩码添加到列表中
        independent_masks.append(pil_mask)

    return independent_masks


def dilated_mask(mask, size=2):
    # 将图像转换为NumPy数组
    mask_array = np.array(mask)
    # 将图像的像素值二值化，确保掩码为布尔值
    mask_binary = mask_array > 128  # 假设像素值>128为前景，<128为背景
    # 膨胀操作，膨胀2个像素
    dilated_mask = binary_dilation(mask_binary, iterations=size)
    # 将布尔数组转换回0和255的格式
    dilated_mask = np.uint8(dilated_mask) * 255
    # 将膨胀后的结果转换回PIL图像
    return Image.fromarray(dilated_mask)
