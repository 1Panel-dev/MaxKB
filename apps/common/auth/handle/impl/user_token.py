# coding=utf-8
"""
    @project: maxkb
    @Author：虎虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  用户认证
"""
from django.db.models import QuerySet
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import Auth, RoleConstants
from common.exception.app_exception import AppAuthenticationFailed
from users.models import User
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class UserToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        if auth_details is None:
            return False
        return True

    def handle(self, request, token: str, get_token_details):
        cache_token = cache.get(token, version=Cache_Version.TOKEN)
        if cache_token is None:
            raise AppAuthenticationFailed(1002, _('Login expired'))
        auth_details = get_token_details()
        user = QuerySet(User).get(id=auth_details['id'])
        role = RoleConstants[user.role]
        return user, Auth([], [],
                          client_id=str(user.id),
                          client_type=AuthenticationType.SYSTEM_USER.value, current_role=role)
