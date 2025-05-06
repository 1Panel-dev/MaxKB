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

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.permission_constants import get_default_workspace_user_role_mapping_list, RoleConstants, \
    ResourcePermissionGroup, ResourcePermissionRole, ResourceAuthType
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from common.utils.split_model import group_by
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from system_manage.models import WorkspaceUserResourcePermission, AuthTargetType


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
    auth_target_type = serializers.ChoiceField(required=True, choices=AuthTargetType.choices, label="授权资源")
    target_id = serializers.CharField(required=True, label=_('target id'))
    auth_type = serializers.ChoiceField(required=True, choices=ResourceAuthType.choices, label="授权类型")
    permission = PermissionSerializer(required=True, many=False)


class UpdateUserResourcePermissionRequest(serializers.Serializer):
    user_resource_permission_list = UpdateTeamMemberItemPermissionSerializer(required=True, many=True)

    def is_valid(self, *, workspace_id=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        user_resource_permission_list = self.data.get("user_resource_permission_list")
        illegal_target_id_list = select_list(
            get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', 'check_member_permission_target_exists.sql')),
            [json.dumps(user_resource_permission_list), workspace_id])
        if illegal_target_id_list is not None and len(illegal_target_id_list) > 0:
            raise AppApiException(500,
                                  _('Non-existent application|knowledge base id[') + str(illegal_target_id_list) + ']')


class UserResourcePermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def get_queryset(self):
        return {
            "knowledge_query_set": QuerySet(Knowledge)
            .filter(workspace_id=self.data.get('workspace_id')),
            'workspace_user_resource_permission_query_set': QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id=self.data.get('workspace_id'))
        }

    def list(self, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        # 用户权限列表
        user_resource_permission_list = native_search(self.get_queryset(), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', 'get_user_resource_permission.sql')))
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        workspace_model = DatabaseModelManage.get_model("workspace_model")
        if workspace_user_role_mapping_model and workspace_model:
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user.id,
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
                                 'permission': {ResourcePermissionGroup.VIEW.value: True,
                                                ResourcePermissionGroup.MANAGE.value: True,
                                                ResourcePermissionRole.ROLE.value: True}},
                    user_resource_permission_list))
        return group_by([{**user_resource_permission, 'permission': {
            permission: True if user_resource_permission.get('permission_list').__contains__(permission) else False for
            permission in
            [ResourcePermissionGroup.VIEW.value, ResourcePermissionGroup.MANAGE.value,
             ResourcePermissionRole.ROLE.value]}}
            for user_resource_permission in user_resource_permission_list],
            key=lambda item: item.get('auth_target_type'))

    def edit(self, instance, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UpdateUserResourcePermissionRequest(data=instance).is_valid(raise_exception=True,
                                                                        workspace_id=self.data.get('workspace_id'))
        workspace_id = self.data.get("workspace_id")
        update_list = []
        save_list = []
        user_resource_permission_list = instance.get('user_resource_permission_list')
        workspace_user_resource_permission_exist_list = QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=workspace_id)
        for user_resource_permission in user_resource_permission_list:
            exist_list = [user_resource_permission_exist for user_resource_permission_exist in
                          workspace_user_resource_permission_exist_list if
                          user_resource_permission.get('target_id') == str(user_resource_permission_exist.target)]
            if len(exist_list) > 0:
                exist_list[0].permission_list = [key for key in user_resource_permission.get('permission').keys() if
                                                 user_resource_permission.get('permission').get(key)]
                update_list.append(exist_list[0])
            else:
                save_list.append(WorkspaceUserResourcePermission(target=user_resource_permission.get('target_id'),
                                                                 auth_target_type=user_resource_permission.get(
                                                                     'auth_target_type'),
                                                                 permission_list=[key for key in
                                                                                  user_resource_permission.get(
                                                                                      'permission').keys() if
                                                                                  user_resource_permission.get(
                                                                                      'permission').get(key)],
                                                                 workspace_id=workspace_id,
                                                                 user_id=user.id,
                                                                 auth_type=user_resource_permission.get('auth_type')))
        # 批量更新
        QuerySet(WorkspaceUserResourcePermission).bulk_update(update_list, ['permission_list']) if len(
            update_list) > 0 else None
        # 批量插入
        QuerySet(WorkspaceUserResourcePermission).bulk_create(save_list) if len(save_list) > 0 else None
        return True
