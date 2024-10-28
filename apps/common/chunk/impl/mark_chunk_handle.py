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

max_chunk_len = 256
split_chunk_pattern = r'.{1,%d}[。| |\\.|！|;|；|!|\n]' % max_chunk_len
max_chunk_pattern = r'.{1,%d}' % max_chunk_len


class MarkChunkHandle(IChunkHandle):
    def handle(self, chunk_list: List[str]):
        result = []
        for chunk in chunk_list:
            chunk_result = re.findall(split_chunk_pattern, chunk, flags=re.DOTALL)
            for c_r in chunk_result:
                if len(c_r.strip()) > 0:
                    result.append(c_r.strip())

            other_chunk_list = re.split(split_chunk_pattern, chunk, flags=re.DOTALL)
            for other_chunk in other_chunk_list:
                if len(other_chunk) > 0:
                    if len(other_chunk) < max_chunk_len:
                        if len(other_chunk.strip()) > 0:
                            result.append(other_chunk.strip())
                    else:
                        max_chunk_list = re.findall(max_chunk_pattern, other_chunk, flags=re.DOTALL)
                        for m_c in max_chunk_list:
                            if len(m_c.strip()) > 0:
                                result.append(m_c.strip())

        return result
