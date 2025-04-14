# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： result.py
    @date：2025/4/14 15:18
    @desc:
"""
from typing import List

from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import status


class Page(dict):
    """
    分页对象
    """

    def __init__(self, total: int, records: List, current_page: int, page_size: int, **kwargs):
        super().__init__(**{'total': total, 'records': records, 'current': current_page, 'size': page_size})


class Result(JsonResponse):
    charset = 'utf-8'
    """
     接口统一返回对象
    """

    def __init__(self, code=200, message=_('Success'), data=None, response_status=status.HTTP_200_OK, **kwargs):
        back_info_dict = {"code": code, "message": message, 'data': data}
        super().__init__(data=back_info_dict, status=response_status, **kwargs)


def success(data, **kwargs):
    """
    获取一个成功的响应对象
    :param data: 接口响应数据
    :return: 请求响应对象
    """
    return Result(data=data, **kwargs)


def error(message, **kwargs):
    """
    获取一个失败的响应对象
    :param message: 错误提示
    :return: 接口响应对象
    """
    return Result(code=500, message=message, **kwargs)
