# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2023/10/16 16:42
    @desc:
"""
import hashlib
import importlib
from functools import reduce
from typing import Dict, List

from django.db.models import QuerySet

from ..exception.app_exception import AppApiException
from ..models.db_model_manage import DBModelManage


def sub_array(array: List, item_num=10):
    result = []
    temp = []
    for item in array:
        temp.append(item)
        if len(temp) >= item_num:
            result.append(temp)
            temp = []
    if len(temp) > 0:
        result.append(temp)
    return result


def query_params_to_single_dict(query_params: Dict):
    return reduce(lambda x, y: {**x, **y}, list(
        filter(lambda item: item is not None, [({key: value} if value is not None and len(value) > 0 else None) for
                                               key, value in
                                               query_params.items()])), {})


def get_exec_method(clazz_: str, method_: str):
    """
    根据 class 和method函数 获取执行函数
    :param clazz_:   class 字符串
    :param method_:  执行函数
    :return: 执行函数
    """
    clazz_split = clazz_.split('.')
    clazz_name = clazz_split[-1]
    package = ".".join([clazz_split[index] for index in range(len(clazz_split) - 1)])
    package_model = importlib.import_module(package)
    return getattr(getattr(package_model, clazz_name), method_)


def flat_map(array: List[List]):
    """
    将二位数组转为一维数组
    :param array: 二维数组
    :return: 一维数组
    """
    result = []
    for e in array:
        result += e
    return result


def password_encrypt(raw_password):
    """
    密码 md5加密
    :param raw_password: 密码
    :return:  加密后密码
    """
    md5 = hashlib.md5()  # 2，实例化md5() 方法
    md5.update(raw_password.encode())  # 3，对字符串的字节类型加密
    result = md5.hexdigest()  # 4，加密
    return result


def post(post_function):
    def inner(func):
        def run(*args, **kwargs):
            result = func(*args, **kwargs)
            return post_function(*result)

        return run

    return inner


def valid_license(model=None, count=None, message=None):
    def inner(func):
        def run(*args, **kwargs):
            xpack_cache = DBModelManage.get_model('xpack_cache')
            is_license_valid = xpack_cache.get('XPACK_LICENSE_IS_VALID', False) if xpack_cache is not None else False
            record_count = QuerySet(model).count()

            if not is_license_valid and record_count >= count:
                error_message = message or f'超出限制{count}, 请联系我们（https://fit2cloud.com/）。'
                raise AppApiException(400, error_message)

            return func(*args, **kwargs)

        return run

    return inner
