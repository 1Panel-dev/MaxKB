# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： is_not_null_compare.py
    @date：2024/6/28 10:45
    @desc:
"""
from typing import List

from application.flow.step_node.condition_node.compare import Compare


class IsNotNullCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'is_not_null':
            return True

    def compare(self, source_value, compare, target_value):
        return source_value is not None and len(source_value) > 0
