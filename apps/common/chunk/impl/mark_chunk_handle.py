# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： mark_chunk_handle.py
    @date：2024/7/23 16:52
    @desc:
"""
import re
from typing import List

from common.chunk.i_chunk_handle import IChunkHandle

split_chunk_pattern = "！|。|\n|；|;"


class MarkChunkHandle(IChunkHandle):
    def handle(self, chunk_list: List[str]):
        result = []
        for chunk in chunk_list:
            base_chunk = re.split(split_chunk_pattern, chunk)
            base_chunk = [chunk.strip() for chunk in base_chunk if len(chunk.strip()) > 0]
            result = [*result, *base_chunk]
        return result
