# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： cache_util.py
@date：2024/7/24 19:23
@desc:
"""

from django.core.cache import cache
from common.constants.cache_version import Cache_Version


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
                cache_instance.add(key, data, timeout=None, version=version)
                return data
            data = get_data(*args, **kwargs)
            cache_instance.set(key, data, timeout=None, version=version)
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


def _normalize_user_ids(user_ids):
    """将用户ID可迭代对象规整为字符串列表，剔除空值。"""
    if isinstance(user_ids, (str, bytes)):
        user_ids = [user_ids]
    try:
        iterator = iter(user_ids)
    except TypeError:
        iterator = iter([user_ids])
    normalized = []
    for user_id in iterator:
        if user_id is None:
            continue
        normalized.append(str(user_id))
    return normalized


def _delete_user_cache(user_ids, cache_item):
    user_ids = _normalize_user_ids(user_ids)
    if not user_ids:
        return
    version, get_key = cache_item.value
    cache.delete_many([get_key(user_id) for user_id in user_ids], version=version)


def clear_user_permission_cache(user_ids):
    """
    清理指定用户的权限缓存(PERMISSION_LIST)。
    @param user_ids: 用户ID的可迭代对象
    """
    _delete_user_cache(user_ids, Cache_Version.PERMISSION_LIST)


def clear_user_role_cache(user_ids):
    """
    清理指定用户的角色缓存(ROLE_LIST)。
    @param user_ids: 用户ID的可迭代对象
    """
    _delete_user_cache(user_ids, Cache_Version.ROLE_LIST)


def clear_user_permission_and_role_cache(user_ids):
    """同时清理指定用户的权限缓存与角色缓存。"""
    clear_user_permission_cache(user_ids)
    clear_user_role_cache(user_ids)
