# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： equal_compare.py
    @date：2024/6/7 14:44
    @desc:
"""
from .compare import Compare


class EqualCompare(Compare):

    def compare(self, source_value, compare, target_value):
        return str(source_value) == str(target_value)
