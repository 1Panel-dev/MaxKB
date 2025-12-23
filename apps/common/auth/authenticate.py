# coding=utf-8
"""
    @project: qabot
    @Author：虎虎
    @file： authenticate.py
    @date：2023/9/4 11:16
    @desc:  认证类
"""
from importlib import import_module

from django.conf import settings
from django.core import cache
from django.core import signing
from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import TokenAuthentication

from common.exception.app_exception import AppAuthenticationFailed, AppEmbedIdentityFailed, AppChatNumOutOfBoundsFailed, \
    AppApiException
from common.utils.logger import maxkb_logger

token_cache = cache.caches['default']


class AnonymousAuthentication(TokenAuthentication):
    def authenticate(self, request):
        return None, None


class AnonymousAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = AnonymousAuthentication  # 绑定到你的自定义认证类
    name = "AnonymousAuth"  # 自定义认证名称（显示在 Swagger UI 中）

    def get_security_definition(self, auto_schema):
        # 定义认证方式，这里假设匿名认证不需要凭证
        return {
        }

    def get_security_requirement(self, auto_schema):
        # 返回安全要求（空字典表示无需认证）
        return {}


def new_instance_by_class_path(class_path: str):
    parts = class_path.rpartition('.')
    package_path = parts[0]
    class_name = parts[2]
    module = import_module(package_path)
    HandlerClass = getattr(module, class_name)
    return HandlerClass()


handles = [new_instance_by_class_path(class_path) for class_path in settings.AUTH_HANDLES]
chat_handles = [new_instance_by_class_path(class_path) for class_path in settings.CHAT_AUTH_HANDLES]


class TokenDetails:
    token_details = None
    is_load = False

    def __init__(self, token: str):
        self.token = token

    def get_token_details(self):
        if self.token_details is None and not self.is_load:
            try:
                self.token_details = signing.loads(self.token)
            except Exception as e:
                self.is_load = True
        return self.token_details


class TokenAuth(TokenAuthentication):
    keyword = "Bearer"

    # 重新 authenticate 方法，自定义认证规则
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        # 未认证
        if auth is None:
            raise AppAuthenticationFailed(1003, _('Not logged in, please log in first'))
        if not auth.startswith("Bearer "):
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user'))
        try:
            token = auth[7:]
            token_details = TokenDetails(token)
            for handle in handles:
                if handle.support(request, token, token_details.get_token_details):
                    return handle.handle(request, token, token_details.get_token_details)
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user'))
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if isinstance(e, AppEmbedIdentityFailed) or isinstance(e, AppChatNumOutOfBoundsFailed) or isinstance(e,
                                                                                                                 AppApiException):
                raise e
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user'))


class ChatTokenAuth(TokenAuthentication):
    keyword = "Bearer"

    # 重新 authenticate 方法，自定义认证规则
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        # 未认证
        if auth is None:
            raise AppAuthenticationFailed(1003, _('Not logged in, please log in first'))
        if not auth.startswith("Bearer "):
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user'))
        try:
            token = auth[7:]
            token_details = TokenDetails(token)
            for handle in chat_handles:
                if handle.support(request, token, token_details.get_token_details):
                    return handle.handle(request, token, token_details.get_token_details)
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user'))
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if isinstance(e, AppEmbedIdentityFailed) or isinstance(e, AppChatNumOutOfBoundsFailed) or isinstance(e,
                                                                                                                 AppApiException):
                raise e
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user'))
