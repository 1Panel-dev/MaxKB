# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： static_resource_cache.py
    @date：2024/7/25 11:30
    @desc:
"""
from common.constants.cache_code_constants import CacheCodeConstants
from common.util.cache_util import get_cache


@get_cache(cache_key=lambda index_path: index_path,
           version=CacheCodeConstants.STATIC_RESOURCE_CACHE.value)
def get_index_html(index_path):
    file = open(index_path, "r", encoding='utf-8')
    content = file.read()
    file.close()
    return content
