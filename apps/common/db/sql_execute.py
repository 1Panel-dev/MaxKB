# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： sql_execute.py
    @date：2023/9/25 20:05
    @desc:
"""
from typing import List

from django.db import connection


def sql_execute(sql: str, params):
    """
    执行一条sql
    :param sql:     需要执行的sql
    :param params:  sql参数
    :return:        执行结果
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = list(map(lambda d: d.name, cursor.description))
        res = cursor.fetchall()
        result = list(map(lambda row: dict(list(zip(columns, row))), res))
        cursor.close()
        return result


def update_execute(sql: str, params):
    """
      执行一条sql
      :param sql:     需要执行的sql
      :param params:  sql参数
      :return:        执行结果
      """
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        cursor.close()
        return None


def select_list(sql: str, params: List):
    """
    执行sql 查询列表数据
    :param sql:     需要执行的sql
    :param params:  sql的参数
    :return: 查询结果
    """
    result_list = sql_execute(sql, params)
    if result_list is None:
        return []
    return result_list


def select_one(sql: str, params: List):
    """
    执行sql 查询一条数据
    :param sql:     需要执行的sql
    :param params:  参数
    :return: 查询结果
    """
    result_list = sql_execute(sql, params)
    if result_list is None or len(result_list) == 0:
        return None
    return result_list[0]
