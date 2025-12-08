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
from django.db import models
from django.db.models import QuerySet, Q, TextField
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import get_default_workspace_user_role_mapping_list, RoleConstants, \
    ResourcePermission, ResourcePermissionRole, ResourceAuthType
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search, get_dynamics_model
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from maxkb.settings import edition
from models_provider.models import Model
from system_manage.models import WorkspaceUserResourcePermission
from tools.models import Tool
from users.serializers.user import is_workspace_manage


class PermissionSerializer(serializers.Serializer):
    VIEW = serializers.BooleanField(required=True, label="可读")
    MANAGE = serializers.BooleanField(required=True, label="管理")
    ROLE = serializers.BooleanField(required=True, label="跟随角色")


class UserResourcePermissionItemResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label="主键id")
    name = serializers.CharField(required=True, label="资源名称")
    auth_target_type = serializers.CharField(required=True, label="授权资源")
    user_id = serializers.UUIDField(required=True, label="用户id")
    icon = serializers.CharField(required=True, label="资源图标")
    auth_type = serializers.CharField(required=True, label="授权类型")
    permission = serializers.ChoiceField(required=False, allow_null=True, allow_blank=True,
                                         choices=['NOT_AUTH', 'MANAGE', 'VIEW', 'ROLE'],
                                         label=_('permission'))


class UserResourcePermissionResponse(serializers.Serializer):
    KNOWLEDGE = UserResourcePermissionItemResponse(many=True)


class UpdateTeamMemberItemPermissionSerializer(serializers.Serializer):
    target_id = serializers.CharField(required=True, label=_('target id'))
    permission = serializers.ChoiceField(required=False, allow_null=True, allow_blank=True,
                                         choices=['NOT_AUTH', 'MANAGE', 'VIEW', 'ROLE'],
                                         label=_('permission'))


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
            [json.dumps(user_resource_permission_list), workspace_id, workspace_id, workspace_id, workspace_id,
             workspace_id, workspace_id, workspace_id])
        if illegal_target_id_list is not None and len(illegal_target_id_list) > 0:
            raise AppApiException(500,
                                  _('Non-existent id')+'[' + str(illegal_target_id_list) + ']')


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


class UserResourcePermissionUserListRequest(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('resource name'))
    permission = serializers.MultipleChoiceField(required=False, allow_null=True, allow_blank=True,
                                                 choices=['NOT_AUTH', 'MANAGE', 'VIEW', 'ROLE'],
                                                 label=_('permission'))


class UserResourcePermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.CharField(required=True, label=_('user id'))
    auth_target_type = serializers.CharField(required=True, label=_('resource'))

    def get_queryset(self, instance):
        resource_query_set = QuerySet(
            model=get_dynamics_model({
                'name': models.CharField(),
                "permission": models.CharField(),
            }))
        name = instance.get('name')
        permission = instance.get('permission')
        query_p_list = [None if p == "NOT_AUTH" else p for p in permission]

        if name:
            resource_query_set = resource_query_set.filter(name__contains=name)
        if permission:
            if all([p is None for p in query_p_list]):
                resource_query_set = resource_query_set.filter(permission=None)
            else:
                if any([p is None for p in query_p_list]):
                    resource_query_set = resource_query_set.filter(
                        Q(permission__in=query_p_list) | Q(permission=None))
                else:
                    resource_query_set = resource_query_set.filter(
                        permission__in=query_p_list)
        return {
            'query_set': QuerySet(m_map.get(self.data.get('auth_target_type'))).filter(
                workspace_id=self.data.get('workspace_id')),
            'folder_query_set': QuerySet(m_map.get(self.data.get('auth_target_type'))).filter(
                workspace_id=self.data.get('workspace_id')),
            'workspace_user_resource_permission_query_set': QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id=self.data.get('workspace_id'), user=self.data.get('user_id'),
                auth_target_type=self.data.get('auth_target_type')),
            'resource_query_set': resource_query_set
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

    def auth_resource(self, resource_id: str, is_folder=False):
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
                             ResourcePermission.MANAGE] if (
                    auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP or is_folder) else [
                ResourcePermissionRole.ROLE],
            workspace_id=workspace_id,
            user_id=user_id,
            auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP if is_folder else auth_type
        ).save()
        # 刷新缓存
        version = Cache_Version.PERMISSION_LIST.get_version()
        key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
        cache.delete(key, version=version)
        return True

    def list(self, instance, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UserResourcePermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")
        # 用户权限列表
        user_resource_permission_list = native_search(self.get_queryset(instance), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage", 'sql', sql_map.get(self.data.get('auth_target_type')))))

        return [{**user_resource_permission}
                for user_resource_permission in user_resource_permission_list]

    def page(self, instance, current_page: int, page_size: int, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UserResourcePermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")
        # 用户对应的资源权限分页列表
        user_resource_permission_page_list = native_page_search(current_page, page_size, self.get_queryset(instance),
                                                                get_file_content(
                                                                    os.path.join(PROJECT_DIR, "apps", "system_manage",
                                                                                 'sql', sql_map.get(
                                                                            self.data.get('auth_target_type')))
                                                                ))

        return user_resource_permission_page_list

    def edit(self, instance, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UpdateUserResourcePermissionRequest(data={'user_resource_permission_list': instance}).is_valid(
                raise_exception=True,
                auth_target_type=self.data.get(
                    'auth_target_type'),
                workspace_id=self.data.get('workspace_id'))
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")
        update_list = []
        save_list = []
        targets = [item['target_id'] for item in instance]
        QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=workspace_id,
            user_id=user_id,
            auth_target_type=self.data.get('auth_target_type'),
            target__in=targets
        ).delete()
        workspace_user_resource_permission_exist_list = []
        for user_resource_permission in instance:
            permission = user_resource_permission['permission']
            auth_type, permission_list = permission_map[permission]
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
                                                                 permission_list=permission_list,
                                                                 workspace_id=workspace_id,
                                                                 user_id=user_id,
                                                                 auth_type=auth_type))
        # 批量更新
        QuerySet(WorkspaceUserResourcePermission).bulk_update(update_list, ['permission_list', 'auth_type']) if len(
            update_list) > 0 else None
        # 批量插入
        QuerySet(WorkspaceUserResourcePermission).bulk_create(save_list) if len(save_list) > 0 else None
        version = Cache_Version.PERMISSION_LIST.get_version()
        key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
        cache.delete(key, version=version)
        return instance


class ResourceUserPermissionUserListRequest(serializers.Serializer):
    nick_name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('workspace id'))
    username = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('workspace id'))
    permission = serializers.MultipleChoiceField(required=False, allow_null=True, allow_blank=True,
                                                 choices=['NOT_AUTH', 'MANAGE', 'VIEW', 'ROLE'],
                                                 label=_('permission'))


class ResourceUserPermissionEditRequest(serializers.Serializer):
    user_id = serializers.CharField(required=True, label=_('workspace id'))
    permission = serializers.ChoiceField(required=True, choices=['NOT_AUTH', 'MANAGE', 'VIEW', 'ROLE'],
                                         label=_('permission'))


permission_map = {
    "ROLE": ("ROLE", ["ROLE"]),
    "MANAGE": ("RESOURCE_PERMISSION_GROUP", ["MANAGE", "VIEW"]),
    "VIEW": ("RESOURCE_PERMISSION_GROUP", ["VIEW"]),
    "NOT_AUTH": ("RESOURCE_PERMISSION_GROUP", []),
}


class ResourceUserPermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    target = serializers.CharField(required=True, label=_('resource id'))
    auth_target_type = serializers.CharField(required=True, label=_('resource'))
    users_permission = ResourceUserPermissionEditRequest(required=False, many=True, label=_('users_permission'))

    RESOURCE_MODEL_MAP = {
        'APPLICATION': Application,
        'KNOWLEDGE': Knowledge,
        'TOOL': Tool
    }

    def get_queryset(self, instance, is_x_pack_ee: bool):

        user_query_set = QuerySet(model=get_dynamics_model({
            'nick_name': models.CharField(),
            'username': models.CharField(),
            "permission": models.CharField(),
            "u.id": models.UUIDField(),
            "role": models.CharField(),
            "role_setting.type": models.CharField(),
            "user_role_relation.workspace_id": models.CharField(),

        }))
        nick_name = instance.get('nick_name')
        username = instance.get('username')
        permission = instance.get('permission')
        query_p_list = [None if p == "NOT_AUTH" else p for p in permission]

        workspace_user_resource_permission_query_set = QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=self.data.get('workspace_id'),
            auth_target_type=self.data.get('auth_target_type'),
            target=self.data.get('target'))
        if nick_name:
            user_query_set = user_query_set.filter(nick_name__contains=nick_name)
        if username:
            user_query_set = user_query_set.filter(username__contains=username)
        if permission:
            if all([p is None for p in query_p_list]):
                user_query_set = user_query_set.filter(
                    permission=None)
            else:
                if any([p is None for p in query_p_list]):
                    user_query_set = user_query_set.filter(
                        Q(permission__in=query_p_list) | Q(permission=None))
                else:
                    user_query_set = user_query_set.filter(
                        permission__in=query_p_list)
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        if workspace_user_role_mapping_model:
            user_query_set = user_query_set.filter(
                **{"u.id__in": QuerySet(workspace_user_role_mapping_model).filter(
                    workspace_id=self.data.get('workspace_id')).values("user_id")})
        if is_x_pack_ee:
            user_query_set = user_query_set.filter(
                **{'role_setting.type': "USER", 'user_role_relation.workspace_id': self.data.get('workspace_id')})
        else:
            user_query_set = user_query_set.filter(
                **{'role': "USER"})
        return {
            'workspace_user_resource_permission_query_set': workspace_user_resource_permission_query_set,
            'user_query_set': user_query_set
        }

    def list(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        is_x_pack_ee = self.is_x_pack_ee()
        # 资源的用户授权列表
        resource_user_permission_list = native_search(self.get_queryset(instance, is_x_pack_ee), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "system_manage",
                         'sql',
                         ('get_resource_user_permission_detail_ee.sql' if is_x_pack_ee else
                          'get_resource_user_permission_detail.sql')
                         )
        ))
        return resource_user_permission_list

    @staticmethod
    def is_x_pack_ee():
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
        return workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None

    def page(self, instance, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        # 分页列表
        is_x_pack_ee = self.is_x_pack_ee()
        resource_user_permission_page_list = native_page_search(current_page, page_size,
                                                                self.get_queryset(instance, is_x_pack_ee),
                                                                get_file_content(
                                                                    os.path.join(PROJECT_DIR, "apps", "system_manage",
                                                                                 'sql',
                                                                                 (
                                                                                     'get_resource_user_permission_detail_ee.sql' if is_x_pack_ee else
                                                                                     'get_resource_user_permission_detail.sql')
                                                                                 )
                                                                ))
        return resource_user_permission_page_list

    def get_has_manage_permission_resource_under_folders(self, current_user_id, folder_ids):

        workspace_id = self.data.get("workspace_id")
        auth_target_type = self.data.get("auth_target_type")
        workspace_manage = is_workspace_manage(current_user_id, workspace_id)
        resource_model = self.RESOURCE_MODEL_MAP[auth_target_type]

        if workspace_manage:
            current_user_managed_resources_ids = QuerySet(resource_model).filter(workspace_id=workspace_id,
                                                                                 folder__in=folder_ids).annotate(
                id_str=Cast('id', TextField())
            ).values_list("id_str", flat=True)
        else:
            current_user_managed_resources_ids = QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id=workspace_id, user_id=current_user_id, auth_target_type=auth_target_type,
                target__in=QuerySet(resource_model).filter(workspace_id=workspace_id, folder__in=folder_ids).annotate(
                    id_str=Cast('id', TextField())
                ).values_list("id_str", flat=True),
                permission_list__contains=['MANAGE']).values_list('target', flat=True)

        return current_user_managed_resources_ids

    def edit(self, instance, with_valid=True, current_user_id=None):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionEditRequest(data=instance, many=True).is_valid(
                raise_exception=True)

        workspace_id = self.data.get("workspace_id")
        target = self.data.get("target")
        auth_target_type = self.data.get("auth_target_type")
        users_permission = instance

        users_id = [item["user_id"] for item in users_permission]
        include_children = users_permission[0].get('include_children')
        folder_ids = users_permission[0].get('folder_ids')
        # 删除已存在的对应的用户在该资源下的权限

        if include_children:
            managed_resource_ids = list(
                self.get_has_manage_permission_resource_under_folders(current_user_id, folder_ids)) + folder_ids

        else:
            managed_resource_ids = [target]
        QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=workspace_id,
            target__in=managed_resource_ids,
            auth_target_type=auth_target_type,
            user_id__in=users_id
        ).delete()

        save_list = [
            WorkspaceUserResourcePermission(
                target=resource_id,
                auth_target_type=auth_target_type,
                workspace_id=workspace_id,
                auth_type=permission_map[item['permission']][0],
                user_id=item["user_id"],
                permission_list=permission_map[item['permission']][1]
            )
            for resource_id in managed_resource_ids
            for item in users_permission
        ]

        if save_list:
            QuerySet(WorkspaceUserResourcePermission).bulk_create(save_list)

        version = Cache_Version.PERMISSION_LIST.get_version()
        for user_id in users_id:
            key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
            cache.delete(key, version=version)
        return instance
