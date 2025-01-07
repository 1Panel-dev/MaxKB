# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： page_utils.py
    @date：2024/11/21 10:32
    @desc:
"""
from math import ceil


def page(query_set, page_size, handler, is_the_task_interrupted=lambda: False):
    """

    @param query_set: 查询query_set
    @param page_size: 每次查询大小
    @param handler:   数据处理器
    @param is_the_task_interrupted: 任务是否被中断
    @return:
    """
    query = query_set.order_by("id")
    count = query_set.count()
    for i in range(0, ceil(count / page_size)):
        if is_the_task_interrupted():
            return
        offset = i * page_size
        paragraph_list = query.all()[offset: offset + page_size]
        handler(paragraph_list)


def page_desc(query_set, page_size, handler, is_the_task_interrupted=lambda: False):
    """

    @param query_set: 查询query_set
    @param page_size: 每次查询大小
    @param handler:   数据处理器
    @param is_the_task_interrupted: 任务是否被中断
    @return:
    """
    query = query_set.order_by("id")
    count = query_set.count()
    for i in sorted(range(0, ceil(count / page_size)), reverse=True):
        if is_the_task_interrupted():
            return
        offset = i * page_size
        paragraph_list = query.all()[offset: offset + page_size]
        handler(paragraph_list)
