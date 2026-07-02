# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： IsTrue.py
    @date：2025/4/7 13:38
    @desc:
"""
from .compare import Compare


class IsTrueCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            return source_value is True
        except Exception:
            return False
