# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2023/11/10 10:41
    @desc:
"""
from concurrent.futures import ThreadPoolExecutor

work_thread_pool = ThreadPoolExecutor(5)

embedding_thread_pool = ThreadPoolExecutor(3)


def poxy(poxy_function):
    def inner(args):
        work_thread_pool.submit(poxy_function, args)

    return inner


def embedding_poxy(poxy_function):
    def inner(args):
        embedding_thread_pool.submit(poxy_function, args)

    return inner
