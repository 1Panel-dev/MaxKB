# coding=utf-8
"""
    @project: MaxKB
    @file： authentication.py
    @desc: 适配层,复用 AggregatePermission
"""

from django.utils.translation import gettext_lazy as _

from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import AggregatePermission
from common.auth.struct.permission import Role

from common.exception.app_exception import AppUnauthorizedFailed


def _build(items, request, kwargs, compare) -> AggregatePermission:
    roles, permissions, aggregates = [], [], []
    for it in items:
        if callable(it) and not isinstance(it, AggregatePermission):
            it = it(request, **kwargs)
        if isinstance(it, AggregatePermission):
            aggregates.append(it)
        elif isinstance(it, (RoleConstants, Role)):
            roles.append(it)
        else:
            permissions.append(it)
    return AggregatePermission(roles=roles, permissions=permissions,
                               aggregatePermissions=aggregates, compare=compare)


def get_is_permissions(request, **kwargs):
    def is_permissions(*permission, compare=CompareConstants.OR):
        return _build(permission, request, kwargs, compare).hasPermission(request, **kwargs)

    return is_permissions


def check_batch_permissions(request, id_list, id_key, permissions, compare=CompareConstants.OR, **kwargs):
    if not id_list:
        return []
    kwargs[id_key] = '__workspace_level_pre_check__'
    if _build(permissions, request, kwargs, compare).hasPermission(request, **kwargs):
        return list(id_list)
    result_list = []
    for resource_id in id_list:
        kwargs[id_key] = resource_id
        if _build(permissions, request, kwargs, compare).hasPermission(request, **kwargs):
            result_list.append(resource_id)
    return result_list


def has_permissions(*permission, compare=CompareConstants.OR):
    """接口权限装饰器"""

    def inner(func):
        def run(view, request, **kwargs):
            if _build(permission, request, kwargs, compare).hasPermission(request, **kwargs):
                return func(view, request, **kwargs)
            raise AppUnauthorizedFailed(403, _('No permission to access'))

        return run

    return inner
