# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： contain_compare.py
    @date：2024/6/11 10:02
    @desc:
"""
from .compare import Compare


class ContainCompare(Compare):

    def compare(self, source_value, compare, target_value):
        target_value = str(target_value)

        if isinstance(source_value, str):
            return target_value in source_value
        elif isinstance(source_value, list):
            for item in source_value:
                if str(item) == target_value:
                    return True
            return False
        else:
            return target_value in str(source_value)
