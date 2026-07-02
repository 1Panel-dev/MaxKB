# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： equal_compare.py
    @date：2024/6/7 14:44
    @desc:
"""
from .compare import Compare


class LenEqualCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            return len(source_value) == int(target_value)
        except Exception as e:
            return False
