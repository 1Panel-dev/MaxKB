# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： lt_compare.py
    @date：2024/6/11 9:52
    @desc: 大于比较器
"""
from .compare import Compare


class LenGTCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            return len(source_value) > int(target_value)
        except Exception:
            return False
