# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： start_with.py
    @date：2025/10/20 10:37
    @desc:
"""
from typing import List

from application.flow.compare import Compare


class StartWithCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'start_with':
            return True

    def compare(self, source_value, compare, target_value):
        source_value = str(source_value)
        return source_value.startswith(str(target_value))
