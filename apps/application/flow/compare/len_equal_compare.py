# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： equal_compare.py
    @date：2024/6/7 14:44
    @desc: 长度等于比较器
"""
from .compare import Compare


def compute_length(source_value, target_value) -> list:
    """
    计算长度

    Args:
        source_value: 引用变量
        target_value: 目标长度字符串

    Raises:
        ValueError: 当 target_value 不是数字 或 小于0时，抛出该异常
    """
    # 获取target_value的长度
    target_length = int(target_value) if target_value else 0
    if target_length < 0:
        raise ValueError("The target length must be greater than or equal to 0.")

    # 获取source_value的长度
    try:
        source_length = len(source_value) if source_value is not None else 0
    except Exception:
        # 可计算数字长度
        source_length = len(str(source_value))

    return [source_length, target_length]


class LenEqualCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            # 计算长度
            source_length, target_length = compute_length(source_value, target_value)

            # 长度等于 比较
            return source_length == target_length
        except Exception:
            return False
