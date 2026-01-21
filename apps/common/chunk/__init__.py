# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： __init__.py
    @date：2024/7/23 17:03
    @desc:
"""
from common.chunk.impl.mark_chunk_handle import MarkChunkHandle
from common.chunk.impl.overlap_chunk_handle import OverlapChunkHandle

handles = [OverlapChunkHandle(), MarkChunkHandle()]


def text_to_chunk(text: str, chunk_size: int = 800):
    chunk_list = [text]
    for handle in handles:
        chunk_list = handle.handle(chunk_list, chunk_size)
    return chunk_list
