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
from common.auth.constants.role_constants import RoleConstants
from common.constants.resource_permission_constants import ResourceAuthType, ResourcePermissionConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search, get_dynamics_model
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from maxkb.settings import edition
from models_provider.models import Model
from system_manage.models import WorkspaceUserResourcePermission, WorkspaceUserGroupResourcePermission
from tools.models import Tool
from users.models.user_group import SystemUserGroupRelation


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
    permission = serializers.ChoiceField(
        required=False,
        allow_null=True,
        allow_blank=True,
        choices=["NOT_AUTH", "MANAGE", "VIEW", "ROLE"],
        label=_("permission"),
    )


class UserResourcePermissionResponse(serializers.Serializer):
    KNOWLEDGE = UserResourcePermissionItemResponse(many=True)


class UpdateTeamMemberItemPermissionSerializer(serializers.Serializer):
    target_id = serializers.CharField(required=True, label=_("target id"))
    permission = serializers.ChoiceField(
        required=False,
        allow_null=True,
        allow_blank=True,
        choices=["NOT_AUTH", "MANAGE", "VIEW", "ROLE"],
        label=_("permission"),
    )


class UpdateUserResourcePermissionRequest(serializers.Serializer):
    user_resource_permission_list = UpdateTeamMemberItemPermissionSerializer(required=True, many=True)

    def is_valid(self, *, auth_target_type=None, workspace_id=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        user_resource_permission_list = [
            {"target_id": urp.get("target_id"), "auth_target_type": auth_target_type}
            for urp in self.data.get("user_resource_permission_list")
        ]
        illegal_target_id_list = select_list(
            get_file_content(
                os.path.join(PROJECT_DIR, "apps", "system_manage", "sql", "check_member_permission_target_exists.sql")
            ),
            [
                json.dumps(user_resource_permission_list),
                workspace_id,
                workspace_id,
                workspace_id,
                workspace_id,
                workspace_id,
                workspace_id,
                workspace_id,
            ],
        )
        if illegal_target_id_list is not None and len(illegal_target_id_list) > 0:
            raise AppApiException(500, _("Non-existent id") + "[" + str(illegal_target_id_list) + "]")


m_map = {
    "KNOWLEDGE": Knowledge,
    "TOOL": Tool,
    "MODEL": Model,
    "APPLICATION": Application,
}

sql_map = {
    "KNOWLEDGE": "get_knowledge_user_group_resource_permission.sql",
    "TOOL": "get_tool_user_group_resource_permission.sql",
    "MODEL": "get_model_user_group_resource_permission.sql",
    "APPLICATION": "get_application_user_group_resource_permission.sql",
}


class UserResourcePermissionUserListRequest(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("resource name"))
    permission = serializers.MultipleChoiceField(
        required=False,
        allow_null=True,
        allow_blank=True,
        choices=["NOT_AUTH", "MANAGE", "VIEW", "ROLE"],
        label=_("permission"),
    )


class UserGroupResourcePermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_("workspace id"))
    user_group_id = serializers.CharField(required=True, label=_("User Group id"))
    auth_target_type = serializers.CharField(required=True, label=_("resource"))

    def get_queryset(self, instance):
        resource_query_set = QuerySet(
            model=get_dynamics_model(
                {
                    "name": models.CharField(),
                    "permission": models.CharField(),
                }
            )
        )
        name = instance.get("name")
        permission = instance.get("permission")
        query_p_list = [None if p == "NOT_AUTH" else p for p in permission]

        if name:
            resource_query_set = resource_query_set.filter(name__contains=name)
        if permission:
            if all([p is None for p in query_p_list]):
                resource_query_set = resource_query_set.filter(permission=None)
            else:
                if any([p is None for p in query_p_list]):
                    resource_query_set = resource_query_set.filter(Q(permission__in=query_p_list) | Q(permission=None))
                else:
                    resource_query_set = resource_query_set.filter(permission__in=query_p_list)
        return {
            "query_set": QuerySet(m_map.get(self.data.get("auth_target_type"))).filter(
                workspace_id=self.data.get("workspace_id")
            ),
            "folder_query_set": QuerySet(m_map.get(self.data.get("auth_target_type"))).filter(
                workspace_id=self.data.get("workspace_id")
            ),
            "workspace_user_group_resource_permission_query_set": QuerySet(WorkspaceUserGroupResourcePermission).filter(
                workspace_id=self.data.get("workspace_id"),
                user_group_id=self.data.get("user_group_id"),
                auth_target_type=self.data.get("auth_target_type"),
            ),
            "resource_query_set": resource_query_set,
        }

    def auth_resource_batch(self, resource_id_list: list):
        self.is_valid(raise_exception=True)
        auth_target_type = self.data.get("auth_target_type")
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")
        wurp = (
            QuerySet(WorkspaceUserResourcePermission)
            .filter(auth_target_type=auth_target_type, workspace_id=workspace_id, user_id=user_id)
            .first()
        )
        auth_type = (
            wurp.auth_type
            if wurp
            else (ResourceAuthType.RESOURCE_PERMISSION_GROUP if edition == "CE" else ResourceAuthType.ROLE)
        )
        workspace_user_resource_permission = [
            WorkspaceUserResourcePermission(
                target=resource_id,
                auth_target_type=auth_target_type,
                permission_list=[ResourcePermissionConstants.VIEW, ResourcePermissionConstants.MANAGE]
                if auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP
                else [ResourcePermissionConstants.ROLE],
                workspace_id=workspace_id,
                user_id=user_id,
                auth_type=auth_type,
            )
            for resource_id in resource_id_list
        ]
        QuerySet(WorkspaceUserResourcePermission).bulk_create(workspace_user_resource_permission)
        # 刷新缓存
        version = Cache_Version.PERMISSION_LIST.get_version()
        key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
        cache.delete(key, version=version)
        return True

    def auth_resource(self, resource_id: str, is_folder=False):
        self.is_valid(raise_exception=True)
        auth_target_type = self.data.get("auth_target_type")
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get("user_id")

        WorkspaceUserResourcePermission(
            target=resource_id,
            auth_target_type=auth_target_type,
            permission_list=[ResourcePermissionConstants.VIEW, ResourcePermissionConstants.MANAGE],
            workspace_id=workspace_id,
            user_id=user_id,
            auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP,
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
        user_group_id = self.data.get("user_group_id")
        # 用户权限列表
        user_resource_permission_list = native_search(
            self.get_queryset(instance),
            get_file_content(
                os.path.join(
                    PROJECT_DIR, "apps", "system_manage", "sql", sql_map.get(self.data.get("auth_target_type"))
                )
            ),
        )

        return [{**user_resource_permission} for user_resource_permission in user_resource_permission_list]

    def page(self, instance, current_page: int, page_size: int, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UserResourcePermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        user_group_id = self.data.get("user_group_id")
        # 用户组对应的资源权限分页列表
        user_resource_permission_page_list = native_page_search(
            current_page,
            page_size,
            self.get_queryset(instance),
            get_file_content(
                os.path.join(
                    PROJECT_DIR, "apps", "system_manage", "sql", sql_map.get(self.data.get("auth_target_type"))
                )
            ),
        )

        return user_resource_permission_page_list

    def edit(self, instance, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            UpdateUserResourcePermissionRequest(data={"user_resource_permission_list": instance}).is_valid(
                raise_exception=True,
                auth_target_type=self.data.get("auth_target_type"),
                workspace_id=self.data.get("workspace_id"),
            )
        workspace_id = self.data.get("workspace_id")
        user_group_id = self.data.get("user_group_id")
        update_list = []
        save_list = []
        targets = [item["target_id"] for item in instance]
        QuerySet(WorkspaceUserGroupResourcePermission).filter(
            workspace_id=workspace_id,
            user_group_id=user_group_id,
            auth_target_type=self.data.get("auth_target_type"),
            target__in=targets,
        ).delete()
        workspace_user_resource_permission_exist_list = []
        for user_resource_permission in instance:
            permission = user_resource_permission["permission"]
            auth_type, permission_list = permission_map[permission]
            exist_list = [
                user_resource_permission_exist
                for user_resource_permission_exist in workspace_user_resource_permission_exist_list
                if user_resource_permission.get("target_id") == str(user_resource_permission_exist.target)
            ]
            if len(exist_list) > 0:
                exist_list[0].permission_list = [
                    key
                    for key in user_resource_permission.get("permission").keys()
                    if user_resource_permission.get("permission").get(key)
                ]
                exist_list[0].auth_type = user_resource_permission.get("auth_type")
                update_list.append(exist_list[0])
            else:
                save_list.append(
                    WorkspaceUserGroupResourcePermission(
                        target=user_resource_permission.get("target_id"),
                        auth_target_type=self.data.get("auth_target_type"),
                        permission_list=permission_list,
                        workspace_id=workspace_id,
                        user_group_id=user_group_id,
                        auth_type=auth_type,
                    )
                )
        # 批量更新
        QuerySet(WorkspaceUserGroupResourcePermission).bulk_update(
            update_list, ["permission_list", "auth_type"]
        ) if len(update_list) > 0 else None
        # 批量插入
        QuerySet(WorkspaceUserGroupResourcePermission).bulk_create(save_list) if len(save_list) > 0 else None
        version = Cache_Version.PERMISSION_LIST.get_version()
        member_user_ids = (
            QuerySet(SystemUserGroupRelation).filter(group_id=user_group_id).values_list("user_id", flat=True)
        )
        for user_id in member_user_ids:
            cache.delete(Cache_Version.PERMISSION_LIST.get_key(user_id=user_id), version=version)
        return instance


class ResourceUserPermissionUserListRequest(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Name"))
    permission = serializers.MultipleChoiceField(
        required=False,
        allow_null=True,
        allow_blank=True,
        choices=["NOT_AUTH", "MANAGE", "VIEW", "ROLE"],
        label=_("permission"),
    )


class ResourceUserPermissionEditRequest(serializers.Serializer):
    user_group_id = serializers.CharField(required=True, label=_("User Group id"))
    permission = serializers.ChoiceField(
        required=True, choices=["NOT_AUTH", "MANAGE", "VIEW", "ROLE"], label=_("permission")
    )


permission_map = {
    "ROLE": ("ROLE", ["ROLE"]),
    "MANAGE": ("RESOURCE_PERMISSION_GROUP", ["MANAGE", "VIEW"]),
    "VIEW": ("RESOURCE_PERMISSION_GROUP", ["VIEW"]),
    "NOT_AUTH": ("RESOURCE_PERMISSION_GROUP", []),
}


class ResourceUserGroupPermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_("workspace id"))
    target = serializers.CharField(required=True, label=_("resource id"))
    auth_target_type = serializers.CharField(required=True, label=_("resource"))
    users_permission = ResourceUserPermissionEditRequest(required=False, many=True, label=_("users_permission"))

    RESOURCE_MODEL_MAP = {"APPLICATION": Application, "KNOWLEDGE": Knowledge, "TOOL": Tool}

    def get_queryset(self, instance):

        user_query_set = QuerySet(
            model=get_dynamics_model(
                {
                    "name": models.CharField(),
                    "permission": models.CharField(),
                    "u.id": models.UUIDField(),
                }
            )
        )
        name = instance.get("name")
        permission = instance.get("permission")
        query_p_list = [None if p == "NOT_AUTH" else p for p in permission]

        workspace_user_resource_permission_query_set = QuerySet(WorkspaceUserGroupResourcePermission).filter(
            workspace_id=self.data.get("workspace_id"),
            auth_target_type=self.data.get("auth_target_type"),
            target=self.data.get("target"),
        )
        if name:
            user_query_set = user_query_set.filter(name__contains=name)
        if permission:
            if all([p is None for p in query_p_list]):
                user_query_set = user_query_set.filter(permission=None)
            else:
                if any([p is None for p in query_p_list]):
                    user_query_set = user_query_set.filter(Q(permission__in=query_p_list) | Q(permission=None))
                else:
                    user_query_set = user_query_set.filter(permission__in=query_p_list)
        return {
            "workspace_user_resource_permission_query_set": workspace_user_resource_permission_query_set,
            "user_query_set": user_query_set,
        }

    def list(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        # 资源的用户授权列表
        resource_user_permission_list = native_search(
            self.get_queryset(instance),
            get_file_content(
                os.path.join(
                    PROJECT_DIR, "apps", "system_manage", "sql", "get_resource_user_group_permission_detail.sql"
                )
            ),
        )
        return resource_user_permission_list

    def page(self, instance, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionUserListRequest(data=instance).is_valid(raise_exception=True)
        resource_user_permission_page_list = native_page_search(
            current_page,
            page_size,
            self.get_queryset(instance),
            get_file_content(
                os.path.join(
                    PROJECT_DIR, "apps", "system_manage", "sql", "get_resource_user_group_permission_detail.sql"
                )
            ),
        )
        return resource_user_permission_page_list

    def get_has_manage_permission_resource_under_folders(self, current_user_id, folder_ids):

        workspace_id = self.data.get("workspace_id")
        auth_target_type = self.data.get("auth_target_type")
        resource_model = self.RESOURCE_MODEL_MAP[auth_target_type]

        from folders.serializers.folder import has_exact_permission_by_role

        permission_id = f"{auth_target_type}:READ+AUTH"

        role_type = RoleConstants.USER.value.__str__()
        has_user_role_exact_permission = has_exact_permission_by_role(
            current_user_id, workspace_id, permission_id, role_type
        )

        permission_list = ["MANAGE"]
        if has_user_role_exact_permission:
            permission_list = ["MANAGE", "ROLE"]

        current_user_managed_resources_ids = (
            QuerySet(WorkspaceUserGroupResourcePermission)
            .filter(
                workspace_id=workspace_id,
                user_id=current_user_id,
                auth_target_type=auth_target_type,
                target__in=QuerySet(resource_model)
                .filter(workspace_id=workspace_id, folder__in=folder_ids)
                .annotate(id_str=Cast("id", TextField()))
                .values_list("id_str", flat=True),
                permission_list__overlap=permission_list,
            )
            .values_list("target", flat=True)
        )

        return current_user_managed_resources_ids

    def edit(self, instance, with_valid=True, current_user_id=None):
        if with_valid:
            self.is_valid(raise_exception=True)
            ResourceUserPermissionEditRequest(data=instance, many=True).is_valid(raise_exception=True)

        workspace_id = self.data.get("workspace_id")
        target = self.data.get("target")
        auth_target_type = self.data.get("auth_target_type")
        users_permission = instance

        user_group_ids = [item["user_group_id"] for item in users_permission]
        include_children = users_permission[0].get("include_children")
        folder_ids = users_permission[0].get("folder_ids")
        # 删除已存在的对应的用户在该资源下的权限

        if include_children:
            managed_resource_ids = (
                list(
                    self.get_has_manage_permission_resource_under_folders(
                        current_user_id,
                        folder_ids,
                    )
                )
                + folder_ids
            )

        else:
            managed_resource_ids = [target]
        QuerySet(WorkspaceUserGroupResourcePermission).filter(
            workspace_id=workspace_id,
            target__in=managed_resource_ids,
            auth_target_type=auth_target_type,
            user_group_id__in=user_group_ids,
        ).delete()

        save_list = [
            WorkspaceUserGroupResourcePermission(
                target=resource_id,
                auth_target_type=auth_target_type,
                workspace_id=workspace_id,
                auth_type=permission_map[item["permission"]][0],
                user_group_id=item["user_group_id"],
                permission_list=permission_map[item["permission"]][1],
            )
            for resource_id in managed_resource_ids
            for item in users_permission
        ]

        if save_list:
            QuerySet(WorkspaceUserResourcePermission).bulk_create(save_list)

        version = Cache_Version.PERMISSION_LIST.get_version()
        for user_group_id in user_group_ids:
            member_user_ids = (
                QuerySet(SystemUserGroupRelation).filter(group_id=user_group_id).values_list("user_id", flat=True)
            )
            for user_id in member_user_ids:
                cache.delete(Cache_Version.PERMISSION_LIST.get_key(user_id=user_id), version=version)
        return instance
