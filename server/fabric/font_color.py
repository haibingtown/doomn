from collections import Counter

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def calculate_dominant_color(image, box, k=3):
    cropped_image = image.crop((box[0][0], box[0][1], box[2][0], box[2][1]))
    preprocessed_image = preprocess_image(cropped_image)
    # preprocessed_image.show()
    text_color = get_dominant_color2(preprocessed_image)
    # print(text_color)
    return text_color
    # return (255,255,255)


# 获取左上角像素的颜色（假设左上角颜色是背景颜色）

def calculate_luminance(color):
    r, g, b = color[:3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def calculate_text_color_by_bg(image, box):
    # (left, upper, right, lower) box 可能是斜的
    left = min(box[0][0], box[1][0], box[2][0], box[3][0])
    upper = min(box[0][1], box[1][1], box[2][1], box[3][1])
    right = max(box[0][0], box[1][0], box[2][0], box[3][0])
    lower = max(box[0][1], box[1][1], box[2][1], box[3][1])
    cropped_image = image.crop((left, upper, right, lower))
    # 计算亮度
    return calculate_text_color(cropped_image)


def calculate_text_color(bg: Image):
    background_color = bg.resize((1, 1)).getpixel((0, 0))
    background_luminance = calculate_luminance(background_color)
    # 根据亮度选择字体颜色
    if background_luminance > 128:
        font_color = (0, 0, 0)
    else:
        font_color = (255, 255, 255)

    return font_color


def rgba_to_rgb(image):
    # 确保图像是RGBA格式
    if image.mode != 'RGBA':
        raise ValueError("Input image must be RGBA format")

    # 创建一个白色背景的RGB图像
    background = Image.new('RGB', image.size, (0, 0, 0))

    # 使用alpha通道作为掩码进行粘贴
    background.paste(image, mask=image.split()[3])  # mask=image.split()[3] 表示使用alpha通道作为掩码

    return background


# 中值颜色算法通过计算图像区域中所有像素的中间值来获取代表颜色。
# 这种方法可以更好地处理包含多个不同颜色的区域，因为它不会像平均值那样被极端颜色值所影响。
def get_median_color(image):
    # 将图像转换为 numpy 数组
    np_image = np.array(image)
    # 计算每个颜色通道的中值
    median_color = np.median(np_image, axis=(0, 1))
    return tuple(map(int, median_color))


# 模式颜色算法找到图像区域中最常出现的颜色。这种方法对于具有少量离散颜色的图像特别有效
def get_mode_color(image):
    # 将图像转换为 RGB 模式并获取所有像素
    pixels = list(image.convert('RGB').getdata())
    # 计算最常出现的颜色
    mode_color = Counter(pixels).most_common(1)[0][0]
    return mode_color


# 主色调提取算法使用聚类算法（如 K-means）来找到图像区域中的主要颜色。这种方法在需要识别图像中主要颜色时特别有用。
def get_dominant_color(image, k=4):
    # 将图像转换为 numpy 数组并重塑为二维数组
    np_image = np.array(image)
    np_image = np_image.reshape((np_image.shape[0] * np_image.shape[1], 3))

    # 使用 K-means 进行聚类
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(np_image)

    # 找到每个簇的大小
    counts = Counter(kmeans.labels_)

    # 找到最大的簇的颜色
    dominant_color = kmeans.cluster_centers_[counts.most_common(1)[0][0]]
    return tuple(map(int, dominant_color))


def preprocess_image(image):
    # 确保图像有三个通道（RGB）
    if image.mode != 'RGB':
        image = image.convert('RGB')
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, None, iterations=2)
    image.putalpha(Image.fromarray(edges))
    return image


def get_text_area(image):
    # 确保图像有三个通道（RGB）
    if image.mode != 'RGB':
        image = image.convert('RGB')
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv2.boundingRect(contours[0])
    return image.crop((x, y, x + w, y + h))


def get_dominant_color2(image, k=3, ignore_background=True):
    # 将图像数据转换为二维数组
    image_np = np.array(image)

    # 筛选透明度大于50的像素
    non_transparent_pixels = image_np[image_np[:, :, 3] > 50]

    pixels = non_transparent_pixels.reshape(-1, 4)

    # 运行K-means算法
    # k = 3  # 选择聚类数，可以调整
    kmeans = KMeans(n_clusters=k, random_state=0).fit(pixels)

    # 获取聚类结果
    labels = kmeans.labels_
    clusters = kmeans.cluster_centers_

    # 找到第二大簇
    unique, counts = np.unique(labels, return_counts=True)
    sorted_indices = np.argsort(counts)  # 从小到大排序
    second_largest_cluster_index = unique[sorted_indices[-2]]  # 倒数第二个是第二大簇

    # 第二大簇的中心
    second_largest_cluster_color = clusters[second_largest_cluster_index]

    # 打印第二大簇的RGB颜色
    second_largest_cluster_rgb = second_largest_cluster_color[:3]  # 取前3个值(RGB)
    print('Second most frequent RGB color:', second_largest_cluster_rgb.astype(int))
    return tuple(second_largest_cluster_rgb.astype(int))
