# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： lock.py
    @date：2023/9/11 11:45
    @desc:
"""
from datetime import timedelta

from django.core.cache import caches

memory_cache = caches['default']


def try_lock(key: str, timeout=None):
    """
    获取锁
    :param key:    获取锁 key
    :param timeout 超时时间
    :return: 是否获取到锁
    """
    return memory_cache.add(key, 'lock', timeout=timedelta(hours=1).total_seconds() if timeout is not None else timeout)


def un_lock(key: str):
    """
    解锁
    :param key: 解锁 key
    :return: 是否解锁成功
    """
    return memory_cache.delete(key)


def lock(lock_key):
    """
    给一个函数上锁
    :param lock_key: 上锁key 字符串|函数  函数返回值为字符串
    :return: 装饰器函数 当前装饰器主要限制一个key只能一个线程去调用 相同key只能阻塞等待上一个任务执行完毕 不同key不需要等待
    """

    def inner(func):
        def run(*args, **kwargs):
            key = lock_key(*args, **kwargs) if callable(lock_key) else lock_key
            try:
                if try_lock(key=key):
                    return func(*args, **kwargs)
            finally:
                un_lock(key=key)

        return run

    return inner
