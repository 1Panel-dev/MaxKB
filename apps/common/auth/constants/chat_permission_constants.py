# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： chat_permission_constants.py
    @date：2026/8/6 16:38
    @desc:
"""
from enum import Enum

from common.auth.constants.group_constants import Group
from common.auth.constants.operate_constants import Operate
from common.auth.struct.permission import Permission


class ChatPermissionConstants(Enum):
    CHAT_USER_ANONYMOUS = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.ANNOTATION_AUTH, 0)
    CHAT_USER_PASSWORD = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.PASSWORD, 1)
    CHAT_USER_LOCAL = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.LOCAL, 2)
    CHAT_USER_CAS = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.CAS, 3)
    CHAT_USER_DINGTALK = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.DINGTALK, 4)
    CHAT_USER_WECOM = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.WECOM, 5)
    CHAT_USER_LARK = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.LARK, 6)
    CHAT_USER_OIDC = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.OIDC, 7)
    CHAT_USER_LDAP = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.LDAP, 8)
    CHAT_USER_OAUTH2 = Permission(Group.CHAT_USER, Group.CHAT_USER, Operate.OAUTH2, 9)

    def get_permission(self):
        return self._build_workspace_permission('application_id')

    def _build_workspace_permission(self, resource_id_key=None):
        def permission_factory(_, kwargs):
            return Permission(group=self.value.group,
                              sub_group=self.value.sub_group,
                              operate=self.value.operate,
                              bit_index=self.value.bit_index,
                              workspace_id=kwargs.get('workspace_id'),
                              resource_id=kwargs.get(resource_id_key) if resource_id_key else None)

        return permission_factory
