# -*- coding: utf-8 -*-

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet, Q, Func, F, TextField
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models.application import Application, ApplicationFolder
from application.serializers.application import ApplicationOperateSerializer
from application.serializers.application_folder import ApplicationFolderTreeSerializer
from common.constants.permission_constants import Group, ResourcePermission, ResourcePermissionRole
from common.exception.app_exception import AppApiException
from folders.api.folder import FolderCreateRequest
from knowledge.models import KnowledgeFolder, Knowledge
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.serializers.knowledge_folder import KnowledgeFolderTreeSerializer
from system_manage.models import WorkspaceUserResourcePermission
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import ToolFolder, Tool
from tools.serializers.tool import ToolSerializer
from tools.serializers.tool_folder import ToolFolderTreeSerializer
from users.serializers.user import is_workspace_manage


def get_source_type(source):
    if source == Group.TOOL.name:
        return Tool
    elif source == Group.APPLICATION.name:
        return Application
    elif source == Group.KNOWLEDGE.name:
        return Knowledge
    else:
        return None


def get_folder_type(source):
    if source == Group.TOOL.name:
        return ToolFolder
    elif source == Group.APPLICATION.name:
        return ApplicationFolder
    elif source == Group.KNOWLEDGE.name:
        return KnowledgeFolder
    else:
        return None


def get_folder_tree_serializer(source):
    if source == Group.TOOL.name:
        return ToolFolderTreeSerializer
    elif source == Group.APPLICATION.name:
        return ApplicationFolderTreeSerializer
    elif source == Group.KNOWLEDGE.name:
        return KnowledgeFolderTreeSerializer
    else:
        return None


FOLDER_DEPTH = 10000


def check_depth(source, parent_id, workspace_id, current_depth=0):
    # Folder 不能超过3层
    Folder = get_folder_type(source)  # noqa

    if parent_id != workspace_id:
        # 计算当前层级
        depth = 1  # 当前要创建的节点算一层
        current_parent_id = parent_id

        # 向上追溯父节点
        while current_parent_id != workspace_id:
            depth += 1
            parent_node = QuerySet(Folder).filter(id=current_parent_id).first()
            if parent_node is None:
                break
            current_parent_id = parent_node.parent_id

        # 验证层级深度
        if depth + current_depth > FOLDER_DEPTH:
            raise serializers.ValidationError(_('Folder depth cannot exceed 10000 levels'))


def get_max_depth(current_node):
    if not current_node:
        return 0

    # 获取所有后代节点
    descendants = current_node.get_descendants()

    if not descendants.exists():
        return 0

    # 获取最大深度
    max_level = descendants.order_by('-level').first().level
    current_level = current_node.level
    max_depth = max_level - current_level

    return max_depth


def has_target_permission(workspace_id, source, user_id, target):
    return QuerySet(WorkspaceUserResourcePermission).filter(workspace_id=workspace_id, user_id=user_id,
                                                            auth_target_type=source, target=target,
                                                            permission_list__contains=['MANAGE']).exists()


class FolderSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_('folder id'))
    name = serializers.CharField(required=True, label=_('folder name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('folder description'))
    user_id = serializers.CharField(required=True, label=_('folder user id'))
    workspace_id = serializers.CharField(required=False, label=_('workspace id'))
    parent_id = serializers.CharField(required=False, label=_('parent id'))

    class Create(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        source = serializers.CharField(required=True, label=_('source'))

        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                FolderCreateRequest(data=instance).is_valid(raise_exception=True)

            workspace_id = self.data.get('workspace_id')
            if not workspace_id:
                workspace_id = 'default'
            parent_id = instance.get('parent_id')
            if not parent_id:
                parent_id = workspace_id
            name = instance.get('name')

            Folder = get_folder_type(self.data.get('source'))  # noqa
            if QuerySet(Folder).filter(name=name, workspace_id=workspace_id, parent_id=parent_id).exists():
                raise serializers.ValidationError(_('Folder name already exists'))
            # Folder 不能超过3层
            check_depth(self.data.get('source'), parent_id, workspace_id)

            folder = Folder(
                id=uuid.uuid7(),
                name=instance.get('name'),
                desc=instance.get('desc'),
                user_id=self.data.get('user_id'),
                workspace_id=workspace_id,
                parent_id=parent_id
            )
            folder.save()

            UserResourcePermissionSerializer(data={
                'workspace_id': self.data.get('workspace_id'),
                'user_id': self.data.get('user_id'),
                'auth_target_type': self.data.get('source')
            }).auth_resource(str(folder.id), is_folder=True)

            return FolderSerializer(folder).data

    class Operate(serializers.Serializer):
        id = serializers.CharField(required=True, label=_('folder id'))
        workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
        source = serializers.CharField(required=True, label=_('source'))
        user_id = serializers.UUIDField(required=True, label=_('user id'))

        @transaction.atomic
        def edit(self, instance):
            self.is_valid(raise_exception=True)
            Folder = get_folder_type(self.data.get('source'))  # noqa
            current_id = self.data.get('id')
            current_node = Folder.objects.get(id=current_id)
            if current_node is None:
                raise serializers.ValidationError(_('Folder does not exist'))
            # 模块间的移动
            parent_id = instance.get('parent_id')
            if parent_id is None:
                parent_id = current_node.parent_id
            # 如果要修改文件夹名称，检查同级目录下是否存在同名文件夹
            new_name = instance.get('name')
            if new_name is not None and new_name != current_node.name:
                if QuerySet(Folder).filter(
                        name=new_name,
                        parent_id=parent_id,
                        workspace_id=current_node.workspace_id
                ).exclude(id=current_id).exists():
                    raise serializers.ValidationError(_('Folder name already exists'))

            edit_field_list = ['name', 'desc']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}

            QuerySet(Folder).filter(id=current_id).update(**edit_dict)
            current_node.refresh_from_db()

            if parent_id is not None and current_id != current_node.workspace_id and current_node.parent_id != parent_id:

                source_type = self.data.get('source')
                if has_target_permission(current_node.workspace_id, source_type, self.data.get('user_id'),
                                         parent_id) or is_workspace_manage(self.data.get('user_id'),
                                                                           current_node.workspace_id):
                    current_depth = get_max_depth(current_node)
                    check_depth(self.data.get('source'), parent_id, current_node.workspace_id, current_depth)
                    parent = Folder.objects.get(id=parent_id)

                    if QuerySet(Folder).filter(name=current_node.name, parent_id=parent_id,
                                               workspace_id=current_node.workspace_id).exists():
                        raise serializers.ValidationError(_('Folder name already exists'))

                    current_node.parent = parent
                    current_node.save()
                    current_node.refresh_from_db()
                else:
                    raise AppApiException(403, _('No permission for the target folder'))

            return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            Folder = get_folder_type(self.data.get('source'))  # noqa
            folder = QuerySet(Folder).filter(id=self.data.get('id')).first()
            return FolderSerializer(folder).data

        @transaction.atomic
        def delete(self):
            self.is_valid(raise_exception=True)
            Folder = get_folder_type(self.data.get('source'))  # noqa
            Source = get_source_type(self.data.get('source'))  # noqa
            folder = Folder.objects.filter(id=self.data.get('id')).first()
            if not folder:
                raise serializers.ValidationError(_('Folder does not exist'))
            if folder.id == folder.workspace_id:
                raise serializers.ValidationError(_('Cannot delete root folder'))

            # 工作空间管理员可以删除
            workspace_manage = is_workspace_manage(self.data.get('user_id'), self.data.get('workspace_id'))
            if workspace_manage:
                nodes = Folder.objects.filter(id=self.data.get('id')).get_descendants(include_self=True)
                for node in nodes:
                    # print(node)
                    # 删除相关的资源
                    self.delete_source(node)
                    # 删除节点
                    node.delete()
            # 普通用户删除的文件夹内全部都得是自己有权限的资源
            else:
                nodes = Folder.objects.filter(id=self.data.get('id')).get_descendants(include_self=True)
                for node in nodes:
                    # 删除相关的资源
                    source_ids = (Source.objects.filter(folder_id=node.id)
                                  .annotate(id_str=Cast('id', TextField()))
                                  .values_list('id_str', flat=True))
                    # 检查文件夹是否存在未授权当前用户的资源
                    auth_list = QuerySet(WorkspaceUserResourcePermission).filter(
                        Q(workspace_id=self.data.get('workspace_id')) &
                        Q(user_id=self.data.get('user_id')) &
                        Q(auth_target_type=self.data.get('source')) &
                        Q(target__in=source_ids) &
                        Q(permission_list__overlap=[ResourcePermission.MANAGE, ResourcePermissionRole.ROLE])
                    ).count()
                    if auth_list != len(source_ids):
                        raise AppApiException(500, _('This folder contains resources that you dont have permission'))
                    self.delete_source(node)
                    node.delete()

        def delete_source(self, node):
            Source = get_source_type(self.data.get('source'))  # noqa
            source_ids = Source.objects.filter(folder_id=node.id).values_list('id', flat=True)
            source = self.data.get('source')

            for source_id in source_ids:
                if source == Group.TOOL.name:
                    ToolSerializer.Operate(data={
                        'workspace_id': self.data.get('workspace_id'),
                        'id': source_id,
                    }).delete()
                elif source == Group.APPLICATION.name:
                    ApplicationOperateSerializer(data={
                        'workspace_id': self.data.get('workspace_id'),
                        'application_id': source_id,
                        'user_id': self.data.get('user_id'),
                    }).delete()
                elif source == Group.KNOWLEDGE.name:
                    KnowledgeSerializer.Operate(data={
                        'workspace_id': self.data.get('workspace_id'),
                        'knowledge_id': source_id,
                        'user_id': self.data.get('user_id'),
                    }).delete()


class FolderTreeSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
    source = serializers.CharField(required=True, label=_('source'))

    @staticmethod
    def _check_tree_integrity(queryset):
        """检查树结构完整性"""
        for folder in queryset:
            if folder.lft >= folder.rght:
                return True  # 需要重建
            if folder.is_leaf_node() and folder.get_children().exists():
                return True  # 需要重建
        return False

    def get_folder_tree(self,
                        current_user, name=None):
        self.is_valid(raise_exception=True)
        Folder = get_folder_type(self.data.get('source'))  # noqa

        # 检查特定工作空间的树结构完整性
        workspace_folders = Folder.objects.filter(workspace_id=self.data.get('workspace_id'))

        # 如果发现数据不一致，重建整个表（这是 MPTT 的限制）
        if self._check_tree_integrity(workspace_folders):
            Folder.objects.rebuild()

        workspace_manage = is_workspace_manage(current_user.id, self.data.get('workspace_id'))

        base_q = Q(workspace_id=self.data.get('workspace_id'))

        if name is not None:
            base_q &= Q(name__contains=name)
        if not workspace_manage:
            base_q &= (Q(id__in=WorkspaceUserResourcePermission.objects.filter(user_id=current_user.id,
                                                                               auth_target_type=self.data.get('source'),
                                                                               workspace_id=self.data.get(
                                                                                   'workspace_id'),
                                                                               permission_list__contains=['VIEW'])
            .values_list(
                'target', flat=True)) | Q(id=self.data.get('workspace_id')))

        nodes = Folder.objects.filter(base_q).get_cached_trees()

        TreeSerializer = get_folder_tree_serializer(self.data.get('source'))  # noqa
        serializer = TreeSerializer(nodes, many=True)
        return [d for d in serializer.data if d.get('id') == d.get('workspace_id')]  # 这是可序列化的字典
