# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： is_null_compare.py
    @date：2024/6/28 10:45
    @desc:
"""
from .compare import Compare


class IsNullCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            return source_value is None or len(source_value) == 0
        except Exception:
            return False
