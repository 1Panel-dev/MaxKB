# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： is_true.py
    @date：2025/4/7 13:38
    @desc: 为真比较器
"""
from .compare import Compare


class IsTrueCompare(Compare):

    def compare(self, source_value, compare, target_value):
        return source_value in (True, 'True', 'true', 1, '1')
