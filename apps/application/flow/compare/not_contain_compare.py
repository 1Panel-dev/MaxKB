# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： contain_compare.py
    @date：2024/6/11 10:02
    @desc: 不包含比较器
"""
from .compare import Compare
from .contain_compare import ContainCompare

# 包含比较器
containCompare = ContainCompare()

class NotContainCompare(Compare):

    def compare(self, source_value, compare, target_value):
        return not containCompare.compare(source_value, compare, target_value)
