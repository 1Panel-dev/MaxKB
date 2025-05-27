# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： contain_compare.py
    @date：2024/6/11 10:02
    @desc:
"""
from typing import List

from application.flow.step_node.condition_node.compare.compare import Compare


class NotContainCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'not_contain':
            return True

    def compare(self, source_value, compare, target_value):
        if isinstance(source_value, str):
            return str(target_value) not in source_value
        return not any([str(item) == str(target_value) for item in source_value])
