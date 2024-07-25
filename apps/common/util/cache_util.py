# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： cache_util.py
    @date：2024/7/24 19:23
    @desc:
"""
from django.core.cache import cache


def get_data_by_default_cache(key: str, get_data, cache_instance=cache, version=None, kwargs=None):
    """
    获取数据, 先从缓存中获取,如果获取不到再调用get_data 获取数据
    @param kwargs:          get_data所需参数
    @param key:             key
    @param get_data:        获取数据函数
    @param cache_instance:  cache实例
    @param version:         版本用于隔离
    @return:
    """
    if kwargs is None:
        kwargs = {}
    if cache_instance.has_key(key, version=version):
        return cache_instance.get(key, version=version)
    data = get_data(**kwargs)
    cache_instance.add(key, data, version=version)
    return data


def set_data_by_default_cache(key: str, get_data, cache_instance=cache, version=None):
    data = get_data()
    cache_instance.set(key, data, version=version)
    return data


def get_cache(cache_key, use_get_data: any = True, cache_instance=cache, version=None):
    def inner(get_data):
        def run(*args, **kwargs):
            key = cache_key(*args, **kwargs) if callable(cache_key) else cache_key
            is_use_get_data = use_get_data(*args, **kwargs) if callable(use_get_data) else use_get_data
            if is_use_get_data:
                if cache_instance.has_key(key, version=version):
                    return cache_instance.get(key, version=version)
                data = get_data(*args, **kwargs)
                cache_instance.add(key, data, version=version)
                return data
            data = get_data(*args, **kwargs)
            cache_instance.set(key, data, version=version)
            return data

        return run

    return inner


def del_cache(cache_key, cache_instance=cache, version=None):
    def inner(func):
        def run(*args, **kwargs):
            key = cache_key(*args, **kwargs) if callable(cache_key) else cache_key
            func(*args, **kwargs)
            cache_instance.delete(key, version=version)

        return run

    return inner
