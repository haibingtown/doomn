import re

import pint

# 创建一个UnitRegistry实例
ureg = pint.UnitRegistry()


def remove_spaces(text: str) -> str:
    return text.replace(" ", "")


def is_number(value: str) -> bool:
    # 去除字符串两端的空格
    value = remove_spaces(value)

    # 尝试将字符串转换为浮点数
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_weight(text: str):
    text = remove_spaces(text)
    if len(text) == 0:
        return False
    try:
        # 尝试解析输入文本为重量单位
        weight = ureg.Quantity(text.lower())
        # 检查是否是重量单位
        return weight.check('[mass]')
    except Exception:
        return False


def is_currency(text: str) -> bool:
    value = remove_spaces(text)

    # 定义正则表达式，用于匹配有效的货币格式
    pattern = r'^(?:([£$€¥]|USD|usd|Usd|元)\s*)?[\d,.，]+\s*(?:([£$€¥]|USD|usd|Usd|元))?$'
    # 使用正则表达式进行匹配
    match = re.match(pattern, value)
    if match:
        # # 从正则表达式中提取值
        # currency_symbol1, integer_part, decimal_part, currency_symbol2 = match.groups()
        #
        # # 检查整数部分
        # if integer_part:
        #     integer_part = integer_part.replace(',', '')
        #     # 确保整数部分是纯数字
        #     if not integer_part.isdigit():
        #         return False
        #
        # # 如果有小数部分，则检查格式是否正确
        # if decimal_part and not decimal_part[1:].isdigit():
        #     return False

        return True
    else:
        return False


def is_length_unit(value: str) -> bool:
    # 定义常见的长度单位
    length_units = ["mm", "cm", "m", "km", "inch", "in", "ft", "foot", "feet", "yard", "mile"]

    # 正则表达式匹配模式
    pattern = r"^\s*([+-]?\d+(\.\d+)?)(\s*({}))\s*$".format("|".join(length_units))

    # 尝试匹配
    match = re.match(pattern, value.strip(), re.IGNORECASE)
    return bool(match)