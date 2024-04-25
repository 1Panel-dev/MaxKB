# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  用户认证
"""
from django.db.models import QuerySet

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import RoleConstants, get_permission_list_by_role, Auth
from common.exception.app_exception import AppAuthenticationFailed
from smartdoc.settings import JWT_AUTH
from users.models import User
from django.core import cache

from users.models.user import get_user_dynamics_permission

token_cache = cache.caches['token_cache']


class UserToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        if auth_details is None:
            return False
        return 'id' in auth_details and auth_details.get('type') == AuthenticationType.USER.value

    def handle(self, request, token: str, get_token_details):
        cache_token = token_cache.get(token)
        if cache_token is None:
            raise AppAuthenticationFailed(1002, "登录过期")
        auth_details = get_token_details()
        user = QuerySet(User).get(id=auth_details['id'])
        # 续期
        token_cache.touch(token, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'].total_seconds())
        rule = RoleConstants[user.role]
        permission_list = get_permission_list_by_role(RoleConstants[user.role])
        # 获取用户的应用和知识库的权限
        permission_list += get_user_dynamics_permission(str(user.id))
        return user, Auth(role_list=[rule],
                          permission_list=permission_list,
                          client_id=str(user.id),
                          client_type=AuthenticationType.USER.value,
                          current_role=rule)
