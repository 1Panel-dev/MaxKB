# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： is_not_true.py
    @date：2025/4/7 13:44
    @desc: 不为真比较器
"""
from .compare import Compare


class IsNotTrueCompare(Compare):

    def compare(self, source_value, compare, target_value):
        return source_value not in (True, 'True', 'true', 1, '1')
