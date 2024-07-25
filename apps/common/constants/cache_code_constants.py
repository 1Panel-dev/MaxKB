# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： cache_code_constants.py
    @date：2024/7/24 18:20
    @desc:
"""
from enum import Enum


class CacheCodeConstants(Enum):
    # 应用ACCESS_TOKEN缓存
    APPLICATION_ACCESS_TOKEN_CACHE = 'APPLICATION_ACCESS_TOKEN_CACHE'
    # 静态资源缓存
    STATIC_RESOURCE_CACHE = 'STATIC_RESOURCE_CACHE'
    # 应用API_KEY缓存
    APPLICATION_API_KEY_CACHE = 'APPLICATION_API_KEY_CACHE'
