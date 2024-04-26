# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_split_handle.py
    @date：2024/3/27 18:13
    @desc:
"""
from abc import ABC, abstractmethod
from typing import List


class BaseSplitHandle(ABC):
    @abstractmethod
    def support(self, file, get_buffer):
        pass

    @abstractmethod
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        pass
