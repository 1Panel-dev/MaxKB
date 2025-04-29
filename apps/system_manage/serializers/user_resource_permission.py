# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 17:17
    @desc:
"""
from django.db.models import QuerySet
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from system_manage.models import WorkspaceUserResourcePermission


class UserResourcePermissionResponse(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceUserResourcePermission
        fields = [
            'id', 'workspace_id', 'user_id', 'auth_target_type', 'target',
            'auth_type', 'permission_list', 'create_time', 'update_time'
        ]


class UserResourcePermissionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        workspace_user_resource_permission_list = QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=workspace_id)
        return [UserResourcePermissionResponse(data=user_resource_permission).data for user_resource_permission in
                workspace_user_resource_permission_list]
