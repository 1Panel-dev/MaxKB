# coding=utf-8
"""
    @project: maxkb
    @Author：wangliang181230
    @file： equal_compare.py
    @date：2026/4/28 20:17
    @desc: 长度不等于比较器
"""
from .compare import Compare
from .len_equal_compare import computeLength


class LenNotEqualCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            # 计算长度
            source_length, target_length = computeLength(source_value, target_value)

            # 长度不等于 比较
            return source_length != target_length
        except Exception:
            return False
