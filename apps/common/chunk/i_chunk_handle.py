# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_chunk_handle.py
    @date：2024/7/23 16:51
    @desc:
"""
from abc import ABC, abstractmethod
from typing import List


class IChunkHandle(ABC):
    @abstractmethod
    def handle(self, chunk_list: List[str]):
        pass
