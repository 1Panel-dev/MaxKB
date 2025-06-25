# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： log.py
    @date：2025/6/4 14:13
    @desc:
"""

from system_manage.models.log_management import Log


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
    user_info = {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "nick_name": user.nick_name,
        "username": user.username,
    }
    # 如果是 User 模型且有 role 属性
    if hasattr(user, 'role'):
        user_info['role'] = user.role
    return user_info


def _get_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    return {
        'path': path,
        'body': body,
        'query': query
    }


def _get_workspace_id(request, kwargs):
    return kwargs.get('workspace_id', 'None')


def log(menu: str, operate, get_user=_get_user, get_ip_address=_get_ip_address, get_details=_get_details,
        get_operation_object=None, get_workspace_id=_get_workspace_id):
    """
    记录审计日志
    @param menu: 操作菜单 str
    @param operate: 操作 str|func 如果是一个函数 入参将是一个request 响应为str def operate(request): return "操作菜单"
    @param get_user: 获取用户
    @param get_ip_address:获取IP地址
    @param get_details: 获取执行详情
    @param get_operation_object: 获取操作对象
    @param get_workspace_id: 获取工作空间id
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
                workspace_id = get_workspace_id(request, kwargs)
                _operate = operate
                if callable(operate):
                    _operate = operate(request)
                # 插入审计日志
                Log(menu=menu, operate=_operate, user=user, status=status, ip_address=ip, details=details,
                    operation_object=operation_object, workspace_id=workspace_id).save()

        return run

    return inner
