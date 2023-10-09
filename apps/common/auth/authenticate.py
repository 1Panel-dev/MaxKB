# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authenticate.py
    @date：2023/9/4 11:16
    @desc:  认证类
"""

from django.core import cache
from django.core import signing
from django.db.models import QuerySet
from rest_framework.authentication import TokenAuthentication

from common.constants.permission_constants import Auth, get_permission_list_by_role, RoleConstants
from common.exception.app_exception import AppAuthenticationFailed
from smartdoc.settings import JWT_AUTH
from users.models.user import User, get_user_dynamics_permission

token_cache = cache.caches['token_cache']


class AnonymousAuthentication(TokenAuthentication):
    def authenticate(self, request):
        return None, None


class TokenAuth(TokenAuthentication):
    # 重新 authenticate 方法，自定义认证规则
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', None
                                )
        # 未认证
        if auth is None:
            raise AppAuthenticationFailed(1003, '未登录,请先登录')
        try:
            # 解析 token
            user = signing.loads(auth)
            if 'id' in user:
                cache_token = token_cache.get(auth)
                if cache_token is None:
                    raise AppAuthenticationFailed(1002, "登录过期")
                user = QuerySet(User).get(id=user['id'])
                # 续期
                token_cache.touch(auth, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'].total_seconds())
                rule = RoleConstants[user.role]
                permission_list = get_permission_list_by_role(RoleConstants[user.role])
                # 获取用户的应用和数据集的权限
                permission_list += get_user_dynamics_permission(str(user.id))
                return user, Auth(role_list=[rule],
                                  permission_list=permission_list)
            else:
                raise AppAuthenticationFailed(1002, "身份验证信息不正确！非法用户")

        except Exception as e:
            raise AppAuthenticationFailed(1002, "身份验证信息不正确！非法用户")
