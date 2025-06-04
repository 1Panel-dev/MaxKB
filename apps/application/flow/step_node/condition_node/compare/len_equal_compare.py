# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： equal_compare.py
    @date：2024/6/7 14:44
    @desc:
"""
from typing import List

from application.flow.step_node.condition_node.compare.compare import Compare


class LenEqualCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'len_eq':
            return True

    def compare(self, source_value, compare, target_value):
        try:
            return len(source_value) == int(target_value)
        except Exception as e:
            return False
