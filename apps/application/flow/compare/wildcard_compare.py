# coding=utf-8
"""
    @project: maxkb
    @Author：wangliang181230
    @file： wildcard_compare.py
    @date：2026/3/30 12:11
    @desc:
"""
from typing import List

from application.flow.compare import Compare

import fnmatch

class WildcardCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'wildcard':
            return True

    def compare(self, source_value, compare, target_value):
        return fnmatch.fnmatch(str(source_value), str(target_value))
