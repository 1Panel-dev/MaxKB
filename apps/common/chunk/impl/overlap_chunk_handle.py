# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： overlap_chunk_handle.py
    @date：2026/01/16
    @desc: Overlapping chunk handler for better context preservation
"""
from typing import List

from common.chunk.i_chunk_handle import IChunkHandle


class OverlapChunkHandle(IChunkHandle):
    def handle(self, chunk_list: List[str], chunk_size: int = 800):
        overlap = 400  # 50% overlap
        result = []
        
        for text in chunk_list:
            if len(text) <= chunk_size:
                result.append(text)
                continue
            
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Find sentence boundary
                if end < len(text):
                    for i in range(end - 1, max(start + chunk_size // 2, end - 100), -1):
                        if text[i] in ['。', '！', '？', '.', '!', '?', '\n']:
                            end = i + 1
                            break
                
                chunk = text[start:end].strip()
                if chunk:
                    result.append(chunk)
                
                if end >= len(text):
                    break
                start = end - overlap if end - overlap > start else end
        
        return result

