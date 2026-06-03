# coding=utf-8
"""
@project: MaxKB
@Author：wangliang181230
@file：type_not_compare.py
@date：2026/5/25 10:01
@desc: “数据类型不是” 比较器
"""
from .compare import Compare


class TypeNotCompare(Compare):

    def compare(self, source_value, compare, target_value):
        try:
            if target_value == "json":
                return not isinstance(source_value, (list, dict))
            elif target_value == "num":
                return not isinstance(source_value, (int, float))
            else:
                return type(source_value).__name__ != target_value
        except Exception:
            return False
