# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_key.py
    @date：2025/7/10 03:02
    @desc:  应用api key认证
"""
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from application.models import ApplicationApiKey, ChatUserType, ApplicationAccessToken
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.auth.struct.auth import Principal, Auth
from common.exception.app_exception import AppAuthenticationFailed


class ApplicationKey(AuthBaseHandle):
    def handle(self, request, token: str, get_token_details):
        application_api_key = QuerySet(ApplicationApiKey).filter(secret_key=token).first()
        if application_api_key is None:
            raise AppAuthenticationFailed(500, _('Secret key is invalid'))
        if not application_api_key.is_active:
            raise AppAuthenticationFailed(500, _('Secret key is invalid'))
        if application_api_key.is_permanent is False and application_api_key.expire_time < timezone.now():
            raise AppAuthenticationFailed(500, _('Secret key is expired'))
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=application_api_key.application_id).first()
        if application_access_token is not None:
            if application_access_token.authentication:
                if application_access_token.authentication_value.get('type',
                                                                     'password') != 'password':
                    raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        return Principal(str(application_api_key.id), ChatUserType.APPLICATION_API_KEY,
                         application_id=str(application_api_key.application_id)), Auth(set(), {})

    def support(self, request, token: str, get_token_details):
        return str(token).startswith("application-") or str(token).startswith('agent-')
