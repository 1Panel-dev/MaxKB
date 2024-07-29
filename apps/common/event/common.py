# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2023/11/10 10:41
    @desc:
"""
from concurrent.futures import ThreadPoolExecutor

from django.core.cache.backends.locmem import LocMemCache

work_thread_pool = ThreadPoolExecutor(5)

embedding_thread_pool = ThreadPoolExecutor(3)

memory_cache = LocMemCache('task', {"OPTIONS": {"MAX_ENTRIES": 1000}})


def poxy(poxy_function):
    def inner(args, **keywords):
        work_thread_pool.submit(poxy_function, args, **keywords)

    return inner


def get_cache_key(poxy_function, args):
    return poxy_function.__name__ + str(args)


def get_cache_poxy_function(poxy_function, cache_key):
    def fun(args, **keywords):
        try:
            poxy_function(args, **keywords)
        finally:
            memory_cache.delete(cache_key)

    return fun


def embedding_poxy(poxy_function):
    def inner(args, **keywords):
        key = get_cache_key(poxy_function, args)
        if memory_cache.has_key(key):
            return
        memory_cache.add(key, None)
        f = get_cache_poxy_function(poxy_function, key)
        embedding_thread_pool.submit(f, args, **keywords)

    return inner
