# coding=utf-8
"""
    @project: maxkb
    @Author：wangliang181230
    @file： regex_compare.py
    @date：2026/3/30 12:11
    @desc:
"""
import re
from typing import List

from application.flow.compare import Compare
from common.cache.mem_cache import MemCache

regex_cache = MemCache('regex', {
    'TIMEOUT': 3600, # 缓存有效期为 1 小时
    'OPTIONS': {
        'MAX_ENTRIES': 500, # 最多缓存 500 个条目
        'CULL_FREQUENCY': 10, # 达到上限时，删除约 1/10 的缓存
    },
})


def compile_and_cache(regex_str):
    regex = regex_cache.get(regex_str)
    if not regex:
        regex = re.compile(regex_str)
        regex_cache.set(regex_str, regex)
    return regex

class RegularExpressionCompare(Compare):

    def support(self, node_id, fields: List[str], source_value, compare, target_value):
        if compare == 'regex':
            return True

    def compare(self, source_value, compare, target_value):
        regex = compile_and_cache(target_value)
        return bool(regex.match(str(source_value)))
