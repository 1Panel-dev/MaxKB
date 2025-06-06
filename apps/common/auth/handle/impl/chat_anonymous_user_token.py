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

from application.models import ApplicationAccessToken, ClientType
from common.auth.common import ChatUserToken

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import RoleConstants, Permission, Group, Operate, Auth
from common.exception.app_exception import AppAuthenticationFailed, ChatException


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
        # 匿名用户 除了/api/application/profile 都需要校验是否开启了密码认证
        if request.path != '/api/application/profile':
            if chat_user_token.authentication.is_auth and not chat_user_token.authentication.auth_passed:
                raise ChatException(1002, _('Authentication information is incorrect'))
        return None, Auth(
            current_role_list=[RoleConstants.CHAT_ANONYMOUS_USER],
            permission_list=[
                Permission(group=Group.APPLICATION,
                           operate=Operate.USE)],
            application_id=application_access_token.application_id,
            client_id=auth_details.get('client_id'),
            client_type=ClientType.ANONYMOUS_USER)
