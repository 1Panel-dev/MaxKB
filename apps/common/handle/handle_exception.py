# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： handle_exception.py
    @date：2023/9/5 19:29
    @desc:
"""
import logging
import traceback

from rest_framework.exceptions import ValidationError, ErrorDetail, APIException
from rest_framework.views import exception_handler

from common.exception.app_exception import AppApiException
from common.response import result


def to_result(key, args, parent_key=None):
    """
    将校验异常 args转换为统一数据
    :param key:       校验key
    :param args:      校验异常参数
    :param parent_key 父key
    :return: 接口响应对象
    """
    error_detail = list(filter(
        lambda d: True if isinstance(d, ErrorDetail) else True if isinstance(d, dict) and len(
            d.keys()) > 0 else False,
        (args[0] if len(args) > 0 else {key: [ErrorDetail('未知异常', code='unknown')]}).get(key)))[0]

    if isinstance(error_detail, dict):
        return list(map(lambda k: to_result(k, args=[error_detail],
                                            parent_key=key if parent_key is None else parent_key + '.' + key),
                        error_detail.keys() if len(error_detail) > 0 else []))[0]

    return result.Result(500 if isinstance(error_detail.code, str) else error_detail.code,
                         message=f"【{key if parent_key is None else parent_key + '.' + key}】为必填参数" if str(
                             error_detail) == "This field is required." else error_detail)


def validation_error_to_result(exc: ValidationError):
    """
    校验异常转响应对象
    :param exc: 校验异常
    :return: 接口响应对象
    """
    try:
        v = find_err_detail(exc.detail)
        if v is None:
            return result.error(str(exc.detail))
        return result.error(str(v))
    except Exception as e:
        return result.error(str(exc.detail))


def find_err_detail(exc_detail):
    if isinstance(exc_detail, ErrorDetail):
        return exc_detail
    if isinstance(exc_detail, dict):
        keys = exc_detail.keys()
        for key in keys:
            _value = exc_detail[key]
            if isinstance(_value, list):
                return find_err_detail(_value)
            if isinstance(_value, ErrorDetail):
                return _value
            if isinstance(_value, dict) and len(_value.keys()) > 0:
                return find_err_detail(_value)
    if isinstance(exc_detail, list):
        for v in exc_detail:
            r = find_err_detail(v)
            if r is not None:
                return r


def handle_exception(exc, context):
    exception_class = exc.__class__
    # 先调用REST framework默认的异常处理方法获得标准错误响应对象
    response = exception_handler(exc, context)
    # 在此处补充自定义的异常处理
    if issubclass(exception_class, ValidationError):
        return validation_error_to_result(exc)
    if issubclass(exception_class, AppApiException):
        return result.Result(exc.code, exc.message, response_status=exc.status_code)
    if issubclass(exception_class, APIException):
        return result.error(exc.detail)
    if response is None:
        logging.getLogger("max_kb_error").error(f'{str(exc)}:{traceback.format_exc()}')
        return result.error(str(exc))
    return response
