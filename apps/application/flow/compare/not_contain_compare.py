# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： contain_compare.py
    @date：2024/6/11 10:02
    @desc:
"""
from typing import List

from application.flow.compare import Compare


class NotContainCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'not_contain':
            return True

    def compare(self, source_value, compare, target_value):
        target_value = str(target_value)

        if isinstance(source_value, str):
            return target_value not in source_value
        elif isinstance(source_value, list):
            for item in source_value:
                if str(item) == target_value:
                    return False
            return True
        else:
            return target_value not in str(source_value)
