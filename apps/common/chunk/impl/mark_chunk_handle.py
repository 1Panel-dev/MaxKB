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
min_chunk_len = 20


class MarkChunkHandle(IChunkHandle):
    def handle(self, chunk_list: List[str]):
        result = []
        for chunk in chunk_list:
            base_chunk = re.split(split_chunk_pattern, chunk)
            base_chunk = [chunk.strip() for chunk in base_chunk if len(chunk.strip()) > 0]
            result_chunk = []
            for c in base_chunk:
                if len(result_chunk) == 0:
                    result_chunk.append(c)
                else:
                    if len(result_chunk[-1]) < min_chunk_len:
                        result_chunk[-1] = result_chunk[-1] + c
                    else:
                        if len(c) < min_chunk_len:
                            result_chunk[-1] = result_chunk[-1] + c
                        else:
                            result_chunk.append(c)
            result = [*result, *result_chunk]
        return result
