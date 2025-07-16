# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_anonymous_user_token.py
    @date：2025/6/6 15:08
    @desc:
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from application.models import ApplicationAccessToken
from common.auth.common import ChatUserToken
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import RoleConstants, Permission, Group, Operate, ChatAuth
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppAuthenticationFailed
from maxkb.settings import edition


class ChatAnonymousUserToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        token_details = get_token_details()
        if token_details is None:
            return False
        return (
                'application_id' in token_details and
                'access_token' in token_details and
                token_details.get('type') == AuthenticationType.CHAT_ANONYMOUS_USER.value)

    def handle(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        chat_user_token = ChatUserToken.new_instance(auth_details)
        application_id = chat_user_token.application_id
        access_token = chat_user_token.access_token
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=application_id).first()
        if application_access_token is None:
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        if not application_access_token.is_active:
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        if not application_access_token.access_token == access_token:
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        if application_access_token.authentication and ['PE', 'EE'].__contains__(edition):
            if chat_user_token.authentication.auth_type != application_access_token.authentication_value.get('type',
                                                                                                             ''):
                raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        return None, ChatAuth(
            current_role_list=[RoleConstants.CHAT_ANONYMOUS_USER],
            permission_list=[
                Permission(group=Group.APPLICATION,
                           operate=Operate.USE)],
            application_id=application_access_token.application_id,
            chat_user_id=chat_user_token.chat_user_id,
            chat_user_type=chat_user_token.chat_user_type)
