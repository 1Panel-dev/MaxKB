# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_anonymous_user_token.py
    @date：2025/6/6 15:08
    @desc:
"""
from functools import reduce

from django.db.models import QuerySet, Q
from django.utils.translation import gettext_lazy as _

from application.models import ApplicationAccessToken, ChatUserType
from common.auth.constants.chat_permission_constants import ChatPermissionConstants, CHAT_PERMISSION_STR_MAP
from common.auth.constants.group_constants import Group
from common.auth.constants.operate_constants import Operate
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.auth.struct.auth import Principal, Auth
from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppUnauthorizedFailed
from system_manage.models import ResourceChatUserGroupAuthorize, ResourceType, ResourceChatUserAuthorize, \
    UserGroupRelation, ChatUser

login_type_list = [Operate.LOCAL.value, Operate.CAS.value, Operate.DINGTALK.value, Operate.WECOM.value,
                   Operate.LARK.value, Operate.OIDC.value, Operate.LDAP.value,
                   Operate.OAUTH2.value]


class ChatUserToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        token_details = get_token_details()
        if token_details is None:
            return False
        return token_details.get('type') == AuthenticationType.CHAT_USER.value

    def handle(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        application_access_token_list = QuerySet(ApplicationAccessToken).filter(
            is_active=True
        )
        _type = ChatUserType.ANONYMOUS_USER
        login_type = auth_details.get('login_type')
        user_id = auth_details.get('user_id')
        application_id = (auth_details.get('kwargs') or {}).get('application_id')
        if login_type.upper() == str(Operate.ANNOTATION_AUTH):
            application_access_token_list = application_access_token_list.filter(authentication=False)
        elif login_type.upper() == str(Operate.PASSWORD):
            application_access_token_list = (application_access_token_list
                                             .filter(authentication=True, authentication_value__type='password'))

        elif login_type_list.__contains__(login_type.upper()):
            _type = ChatUserType.CHAT_USER
            user_group_ids = QuerySet(UserGroupRelation).filter(
                user_id=user_id,
            ).values_list('group_id', flat=True)

            group_qs = QuerySet(ResourceChatUserGroupAuthorize).filter(
                resource_type=ResourceType.APPLICATION,
                is_auth=True,
                user_group_id__in=user_group_ids,
            ).values_list('resource_id', flat=True)

            user_qs = QuerySet(ResourceChatUserAuthorize).filter(
                resource_type=ResourceType.APPLICATION,
                is_auth=True,
                user_id=user_id,
            ).values_list('resource_id', flat=True)
            application_access_token_list = application_access_token_list.filter(
                Q(authentication_value__type='login'),
                Q(authentication_value__login_value__contains=login_type),
                Q(application_id__in=group_qs) | Q(application_id__in=user_qs),
            )
        if application_id:
            application_access_token_list = application_access_token_list.filter(application_id=application_id)
        permissions = {}
        for application_access_token in application_access_token_list:
            permission_list = []
            if application_access_token.authentication:
                authentication_value = application_access_token.authentication_value
                if authentication_value.get('type') == 'password':
                    permission_list.append(ChatPermissionConstants.CHAT_USER_PASSWORD.value)
                elif authentication_value.get('type') == 'login':
                    login_value = authentication_value.get('login_value') or []
                    for _value in login_value:
                        permission_str = f'{Group.CHAT_USER}_{_value.upper()}'
                        permission = CHAT_PERMISSION_STR_MAP.get(permission_str)
                        if permission:
                            permission_list.append(permission.value)

            else:
                permission_list.append(ChatPermissionConstants.CHAT_USER_ANONYMOUS.value)
            k = f"{Group.CHAT_USER}:r:{application_access_token.application_id}"
            permissions[k] = reduce(lambda x, y: x | y, [p.bit() for p in permission_list], 0)
        chat_user = QuerySet(ChatUser).filter(id=user_id).first()
        if application_id:
            # 指定了 application_id（v2 流程）时，直接校验该应用是否有权限，无权限直接抛错，
            # 避免返回一个空权限的 Principal 造成静默失败。
            if not permissions.get(f"{Group.CHAT_USER}:r:{application_id}"):
                raise AppUnauthorizedFailed(403, _('No permission to access'))
            return Principal(auth_details.get('user_id'), _type, application_id=application_id,
                             profile=chat_user), Auth(set(),
                                                      permissions)
        return Principal(auth_details.get('user_id'), _type, profile=chat_user), Auth(set(), permissions)
