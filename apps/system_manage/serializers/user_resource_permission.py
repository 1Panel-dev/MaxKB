# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 17:17
    @desc:
"""
import json
import os

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import get_default_workspace_user_role_mapping_list, RoleConstants, \
    ResourcePermission, ResourcePermissionRole, ResourceAuthType
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from common.utils.split_model import group_by
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from maxkb.settings import edition
from models_provider.models import Model
from system_manage.models import WorkspaceUserResourcePermission, AuthTargetType
from tools.models import Tool
from users.models import User
from users.serializers.user import is_workspace_manage


class PermissionSerializer(serializers.Serializer):
    VIEW = serializers.BooleanField(required=True, label="可读")
    MANAGE = serializers.BooleanField(required=True, label="管理")
    ROLE = serializers.BooleanField(required=True, label="跟随角色")


class UserResourcePermissionItemResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label="主键id")
    name = serializers.CharField(required=True, label="资源名称")
    auth_target_type = serializers.ChoiceField(required=True, choices=AuthTargetType.choices, label="授权资源")
    user_id = serializers.UUIDField(required=True, label="用户id")
    auth_type = serializers.ChoiceField(required=True, choices=ResourceAuthType.choices, label="授权类型")
    permission = PermissionSerializer()


class UserResourcePermissionResponse(serializers.Serializer):
    KNOWLEDGE = UserResourcePermissionItemResponse(many=True)


class UpdateTeamMemberItemPermissionSerializer(serializers.Serializer):
    target_id = serializers.CharField(required=True, label=_('target id'))
    auth_type = serializers.ChoiceField(required=True, choices=ResourceAuthType.choices, label="授权类型")
    permission = PermissionSerializer(required=True, many=False)


class UpdateUserResourcePermissionRequest(serializers.Serializer):
    user_resource_permission_list = UpdateTeamMemberItemPermissionSerializer(required=True, many=True)

    def is_valid(self, *, auth_target_type=None, workspace_id=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        user_resource_permission_list = [{'target_id': urp.get('target_id'), 'auth_target_type': auth_target_type} for
                                         urp in
                                         self.data.get("user_resource_permission_list")]
        illegal_target_id_list = select_list(
            get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', 'check_member_permission_target_exists.sql')),
            [json.dumps(user_resource_permission_list), workspace_id, workspace_id, workspace_id, workspace_id])
        if illegal_target_id_list is not None and len(illegal_target_id_list) > 0:
            raise AppApiException(500,
                                  _('Non-existent id[') + str(illegal_target_id_list) + ']')


m_map = {
    "KNOWLEDGE": Knowledge,
    'TOOL': Tool,
    'MODEL': Model,
    'APPLICATION': Application,
}
sql_map = {
    "KNOWLEDGE": 'get_knowledge_user_resource_permission.sql',
    'TOOL': 'get_tool_user_resource_permission.sql',
    'MODEL': 'get_model_user_resource_permission.sql',
    'APPLICATION': 'get_application_user_resource_permission.sql'
}


class UserResourcePermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.CharField(required=True, label=_('user id'))
    auth_target_type = serializers.CharField(required=True, label=_('resource'))

    def get_queryset(self):
        return {
            'query_set': QuerySet(m_map.get(self.data.get('auth_target_type'))).filter(
                workspace_id=self.data.get('workspace_id')),
            'workspace_user_resource_permission_query_set': QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id=self.data.get('workspace_id'), user=self.data.get('user_id'),
                auth_target_type=self.data.get('auth_target_type'))
        }

    def is_auth(self, resource_id: str):
        self.is_valid(raise_exception=True)
        auth_target_type = self.data.get('auth_target_type')
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get('user_id')
        workspace_manage = is_workspace_manage(user_id, workspace_id)
        if workspace_manage:
            return True
        wurp = QuerySet(WorkspaceUserResourcePermission).filter(auth_target_type=auth_target_type,
                                                                workspace_id=workspace_id, user=user_id,
                                                                target=resource_id).first()
        if wurp is None:
            return False
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")

        if wurp.auth_type == ResourceAuthType.ROLE.value:
            if workspace_user_role_mapping_model and role_permission_mapping_model:
                inner = QuerySet(workspace_user_role_mapping_model).filter(workspace_id=workspace_id, user_id=user_id)
                return QuerySet(role_permission_mapping_model).filter(role_id__in=inner,
                                                                      permission_id=(
                                                                              auth_target_type + ':READ')).exists()
            else:
                return False
        else:
            return wurp.permission_list.__contains__(ResourcePermission.VIEW.value)

    def auth_resource_batch(self, resource_id_list: list):
        self.is_valid(raise_exception=True)
        auth_target_type = self.data.get('auth_target_type')
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get('user_id')
        wurp = QuerySet(WorkspaceUserResourcePermission).filter(auth_target_type=auth_target_type,
                                                                workspace_id=workspace_id, user_id=user_id).first()
        auth_type = wurp.auth_type if wurp else (
            ResourceAuthType.RESOURCE_PERMISSION_GROUP if edition == 'CE' else ResourceAuthType.ROLE)
        workspace_user_resource_permission = [WorkspaceUserResourcePermission(
            target=resource_id,
            auth_target_type=auth_target_type,
            permission_list=[ResourcePermission.VIEW,
                             ResourcePermission.MANAGE] if auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP else [
                ResourcePermissionRole.ROLE],
            workspace_id=workspace_id,
            user_id=user_id,
            auth_type=auth_type
        ) for resource_id in resource_id_list]
        QuerySet(WorkspaceUserResourcePermission).bulk_create(workspace_user_resource_permission)
        # 刷新缓存
        version = Cache_Version.PERMISSION_LIST.get_version()
        key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
        cache.delete(key, version=version)
        return True

    def auth_resource(self, resource_id: str):
        self.is_valid(raise_exception=True)
        auth_target_type = self.data.get('auth_target_type')
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get('user_id')
        wurp = QuerySet(WorkspaceUserResourcePermission).filter(auth_target_type=auth_target_type,
                                                                workspace_id=workspace_id, user_id=user_id).first()
        auth_type = wurp.auth_type if wurp else (
            ResourceAuthType.RESOURCE_PERMISSION_GROUP if edition == 'CE' else ResourceAuthType.ROLE)
        # 自动授权给创建者
        WorkspaceUserResourcePermission(
            target=resource_id,
            auth_target_type=auth_target_type,
            permission_list=[ResourcePermission.VIEW,
                             ResourcePermission.MANAGE] if auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP else [
                ResourcePermissionRole.ROLE],
            workspace_id=workspace_id,
            user_id=user_id,
            auth_type=auth_type
        ).save()
        # 刷新缓存
        version = Cache_Version.PERMISSION_LIST.get_version()
        key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
        cache.delete(key, version=version)
        return True

    def list(self, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")
        # 用户权限列表
        user_resource_permission_list = native_search(self.get_queryset(), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', sql_map.get(self.data.get('auth_target_type')))))
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        workspace_model = DatabaseModelManage.get_model("workspace_model")
        if workspace_user_role_mapping_model and workspace_model:
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user_id,
                                                                                                  workspace_id=workspace_id)
        else:
            workspace_user_role_mapping_list = get_default_workspace_user_role_mapping_list([user.role])
        is_workspace_manage = any(
            [workspace_user_role_mapping for workspace_user_role_mapping in workspace_user_role_mapping_list if
             workspace_user_role_mapping.role_id == RoleConstants.WORKSPACE_MANAGE.value])
        # 如果当前用户是当前工作空间管理员那么就拥有所有权限
        if is_workspace_manage:
            user_resource_permission_list = list(
                map(lambda row: {**row,
                                 'permission': {ResourcePermission.VIEW.value: True,
                                                ResourcePermission.MANAGE.value: True,
                                                ResourcePermissionRole.ROLE.value: True}},
                    user_resource_permission_list))
        return group_by([{**user_resource_permission, 'permission': {
            permission: True if user_resource_permission.get('permission_list').__contains__(permission) else False for
            permission in
            [ResourcePermission.VIEW.value, ResourcePermission.MANAGE.value,
             ResourcePermissionRole.ROLE.value]}}
            for user_resource_permission in user_resource_permission_list],
            key=lambda item: item.get('auth_target_type'))

    def edit(self, instance, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UpdateUserResourcePermissionRequest(data=instance).is_valid(raise_exception=True,
                                                                        auth_target_type=self.data.get(
                                                                            'auth_target_type'),
                                                                        workspace_id=self.data.get('workspace_id'))
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")
        update_list = []
        save_list = []
        user_resource_permission_list = instance.get('user_resource_permission_list')
        QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=workspace_id, user_id=user_id, auth_target_type=self.data.get('auth_target_type')).delete()
        workspace_user_resource_permission_exist_list = []
        for user_resource_permission in user_resource_permission_list:
            exist_list = [user_resource_permission_exist for user_resource_permission_exist in
                          workspace_user_resource_permission_exist_list if
                          user_resource_permission.get('target_id') == str(user_resource_permission_exist.target)]
            if len(exist_list) > 0:
                exist_list[0].permission_list = [key for key in user_resource_permission.get('permission').keys() if
                                                 user_resource_permission.get('permission').get(key)]
                exist_list[0].auth_type = user_resource_permission.get('auth_type')
                update_list.append(exist_list[0])
            else:
                save_list.append(WorkspaceUserResourcePermission(target=user_resource_permission.get('target_id'),
                                                                 auth_target_type=self.data.get('auth_target_type'),
                                                                 permission_list=[key for key in
                                                                                  user_resource_permission.get(
                                                                                      'permission').keys() if
                                                                                  user_resource_permission.get(
                                                                                      'permission').get(key)],
                                                                 workspace_id=workspace_id,
                                                                 user_id=user_id,
                                                                 auth_type=user_resource_permission.get('auth_type')))
        # 批量更新
        QuerySet(WorkspaceUserResourcePermission).bulk_update(update_list, ['permission_list', 'auth_type']) if len(
            update_list) > 0 else None
        # 批量插入
        QuerySet(WorkspaceUserResourcePermission).bulk_create(save_list) if len(save_list) > 0 else None
        version = Cache_Version.PERMISSION_LIST.get_version()
        key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
        cache.delete(key, version=version)
        return True


class ResourceUserPermissionUserListRequest(serializers.Serializer):
    nick_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('workspace id'))
    username = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('workspace id'))

class ResourceUserPermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    target = serializers.CharField(required=True, label=_('resource id'))
    auth_target_type = serializers.CharField(required=True, label=_('resource'))

    def get_queryset(self, instance):
        user_query_set = QuerySet(User)
        nick_name = instance.get('nick_name')
        username = instance.get('username')

        if nick_name:
            user_query_set = user_query_set.filter(nick_name__contains=nick_name)
        if username:
            user_query_set = user_query_set.filter(username__contains=username)

        return {
            'workspace_user_resource_permission_query_set': QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id=self.data.get('workspace_id'),
                auth_target_type=self.data.get('auth_target_type'),
                target=self.data.get('target')),
            'user_query_set': user_query_set
        }

    def list(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        # 资源的用户授权列表
        resource_user_permission_list = native_search(self.get_queryset(instance), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', 'get_resource_user_permission_detail.sql')
        ))
        return resource_user_permission_list

    def page(self, instance, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        # 分页列表
        resource_user_permission_page_list = native_page_search(current_page, page_size, self.get_queryset(instance),
                                                                get_file_content(
                                                                    os.path.join(PROJECT_DIR, "apps", "system_manage",
                                                                                 'sql',
                                                                                 'get_resource_user_permission_detail.sql')
                                                                ))
        return resource_user_permission_page_list

    def edit(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
