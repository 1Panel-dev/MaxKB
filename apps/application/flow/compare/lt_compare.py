# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： lt_compare.py
    @date：2024/6/11 9:52
    @desc: 小于比较器
"""
from .compare import Compare


class LTCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            return float(source_value) < float(target_value)
        except Exception:
            try:
                return str(source_value) < str(target_value)
            except Exception:
                pass
            return False
