# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： log.py
    @date：2025/3/14 16:09
    @desc:
"""
from gettext import gettext

from setting.models.log_management import Log


def _get_ip_address(request):
    """
    获取ip地址
    @param request:
    @return:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _get_user(request):
    """
    获取用户
    @param request:
    @return:
    """
    user = request.user
    if user is None:
        return {

        }
    return {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "nick_name": user.nick_name,
        "username": user.username,
        "role": user.role,
    }


def _get_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    return {
        'path': path,
        'body': body,
        'query': query
    }


def log(menu: str, operate, get_user=_get_user, get_ip_address=_get_ip_address, get_details=_get_details,
        get_operation_object=None):
    """
    记录审计日志
    @param menu: 操作菜单 str
    @param operate: 操作 str|func 如果是一个函数 入参将是一个request 响应为str def operate(request): return "操作菜单"
    @param get_user: 获取用户
    @param get_ip_address:获取IP地址
    @param get_details: 获取执行详情
    @param get_operation_object: 获取操作对象
    @return:
    """

    def inner(func):
        def run(view, request, **kwargs):
            status = 200
            operation_object = {}
            try:
                if get_operation_object is not None:
                    operation_object = get_operation_object(request, kwargs)
            except Exception as e:
                pass
            try:
                return func(view, request, **kwargs)
            except Exception as e:
                status = 500
                raise e
            finally:
                ip = get_ip_address(request)
                user = get_user(request)
                details = get_details(request)
                _operate = operate
                if callable(operate):
                    _operate = operate(request)
                # 插入审计日志
                Log(menu=menu, operate=_operate, user=user, status=status, ip_address=ip, details=details,
                    operation_object=operation_object).save()

        return run

    return inner
