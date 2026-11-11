# coding=utf-8
"""
    @project: maxkb
    @Author：wangliang181230
    @file： regex_compare.py
    @date：2026/3/30 12:11
    @desc:
"""
import regex

from .compare import Compare
from common.cache.mem_cache import MemCache

match_cache = MemCache('regex', {
    'TIMEOUT': 3600,  # 缓存有效期为 1 小时
    'OPTIONS': {
        'MAX_ENTRIES': 500,  # 最多缓存 500 个条目
        'CULL_FREQUENCY': 10,  # 达到上限时，删除约 1/10 的缓存
    },
})

MAX_PATTERN_LENGTH = 4096
MAX_MATCH_LENGTH = 65536
MATCH_TIMEOUT = 0.1


def compile_and_cache(pattern):
    match = match_cache.get(pattern)
    if not match:
        match = regex.compile(pattern, regex.VERSION0).fullmatch
        match_cache.set(pattern, match)
    return match


class RegexCompare(Compare):

    def compare(self, source_value, compare, target_value):
        pattern, subject = str(target_value), str(source_value)
        if len(pattern) > MAX_PATTERN_LENGTH or len(subject) > MAX_MATCH_LENGTH:
            return False
        try:
            match = compile_and_cache(pattern)
            return bool(match(subject, timeout=MATCH_TIMEOUT, concurrent=True))
        except (TimeoutError, regex.error, RecursionError):
            return False
