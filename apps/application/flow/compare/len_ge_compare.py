# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： lt_compare.py
    @date：2024/6/11 9:52
    @desc: 长度大于等于比较器
"""
from .compare import Compare
from .len_equal_compare import computeLength


class LenGECompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            # 计算长度
            source_length, target_length = computeLength(source_value, target_value)

            # 长度大于等于 比较
            return source_length >= target_length
        except Exception:
            return False
