# coding=utf-8
"""
    @project: maxkb
    @Author：wangliang181230
    @file： not_equal_compare.py
    @date：2026/3/17 9:41
    @desc:
"""
from .compare import Compare


class NotEqualCompare(Compare):

    def compare(self, source_value, compare, target_value):
        return str(source_value) != str(target_value)
