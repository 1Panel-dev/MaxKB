# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： compare.py
    @date：2024/6/7 14:37
    @desc:
"""
from abc import abstractmethod
from typing import List


class Compare:
    @abstractmethod
    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        pass

    @abstractmethod
    def compare(self, source_value, compare, target_value):
        pass
