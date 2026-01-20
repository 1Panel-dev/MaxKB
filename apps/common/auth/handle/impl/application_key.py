# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_key.py
    @date：2025/7/10 03:02
    @desc:  应用api key认证
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from application.models import ApplicationApiKey, ChatUserType, ApplicationAccessToken
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.permission_constants import Permission, Group, Operate, RoleConstants, ChatAuth
from common.exception.app_exception import AppAuthenticationFailed


class ApplicationKey(AuthBaseHandle):
    def handle(self, request, token: str, get_token_details):
        application_api_key = QuerySet(ApplicationApiKey).filter(secret_key=token).first()
        if application_api_key is None:
            raise AppAuthenticationFailed(500, _('Secret key is invalid'))
        if not application_api_key.is_active:
            raise AppAuthenticationFailed(500, _('Secret key is invalid'))
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=application_api_key.application_id).first()
        if application_access_token is not None:
            if application_access_token.authentication:
                if application_access_token.authentication_value.get('type',
                                                                     'password') != 'password':
                    raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        return None, ChatAuth(
            current_role_list=[RoleConstants.CHAT_ANONYMOUS_USER],
            permission_list=[
                Permission(group=Group.APPLICATION,
                           operate=Operate.READ)],
            application_id=application_api_key.application_id,
            chat_user_id=str(application_api_key.id),
            chat_user_type=ChatUserType.ANONYMOUS_USER.value)

    def support(self, request, token: str, get_token_details):
        return str(token).startswith("application-") or str(token).startswith('agent-')
