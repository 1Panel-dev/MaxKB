# coding=utf-8
"""
    @project: maxkb
    @Author：wangliang181230
    @file： equal_compare.py
    @date：2026/4/28 20:17
    @desc: 长度不等于比较器
"""
from .compare import Compare
from .len_equal_compare import LenEqualCompare


# 长度相等比较器
lenEqualCompare = LenEqualCompare()


class LenNotEqualCompare(Compare):

    def compare(self, source_value, compare, target_value):
        # 长度不等于比较
        return not lenEqualCompare.compare(source_value, compare, target_value)
