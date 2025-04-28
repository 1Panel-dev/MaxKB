# -*- coding: utf-8 -*-

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet, Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.permission_constants import Group
from folders.api.folder import FolderCreateRequest
from knowledge.models import KnowledgeFolder
from knowledge.serializers.knowledge_folder import KnowledgeFolderTreeSerializer
from tools.models import ToolFolder
from tools.serializers.tool_folder import ToolFolderTreeSerializer


def get_folder_type(source):
    if source == Group.TOOL.name:
        return ToolFolder
    elif source == Group.APPLICATION.name:
        # todo app folder
        return None
    elif source == Group.KNOWLEDGE.name:
        return KnowledgeFolder
    else:
        return None


def get_folder_tree_serializer(source):
    if source == Group.TOOL.name:
        return ToolFolderTreeSerializer
    elif source == Group.APPLICATION.name:
        # todo app folder
        return None
    elif source == Group.KNOWLEDGE.name:
        return KnowledgeFolderTreeSerializer
    else:
        return None


FOLDER_DEPTH = 2  # Folder 不能超过3层


def check_depth(source, parent_id, current_depth=0):
    # Folder 不能超过3层
    Folder = get_folder_type(source)

    if parent_id != 'root':
        # 计算当前层级
        depth = 1  # 当前要创建的节点算一层
        current_parent_id = parent_id

        # 向上追溯父节点
        while current_parent_id != 'root':
            depth += 1
            parent_node = QuerySet(Folder).filter(id=current_parent_id).first()
            if parent_node is None:
                break
            current_parent_id = parent_node.parent_id

        # 验证层级深度
        if depth + current_depth > FOLDER_DEPTH:
            raise serializers.ValidationError(_('Folder depth cannot exceed 3 levels'))


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


class FolderSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_('folder id'))
    name = serializers.CharField(required=True, label=_('folder name'))
    user_id = serializers.CharField(required=True, label=_('folder user id'))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('workspace id'))
    parent_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('parent id'))

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        source = serializers.CharField(required=True, label=_('source'))

        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                FolderCreateRequest(data=instance).is_valid(raise_exception=True)

            workspace_id = self.data.get('workspace_id', 'default')
            parent_id = instance.get('parent_id', 'root')
            name = instance.get('name')

            Folder = get_folder_type(self.data.get('source'))
            if QuerySet(Folder).filter(name=name, workspace_id=workspace_id, parent_id=parent_id).exists():
                raise serializers.ValidationError(_('Folder name already exists'))
            # Folder 不能超过3层
            check_depth(self.data.get('source'), parent_id)

            folder = Folder(
                id=uuid.uuid7(),
                name=instance.get('name'),
                user_id=self.data.get('user_id'),
                workspace_id=workspace_id,
                parent_id=parent_id
            )
            folder.save()
            return FolderSerializer(folder).data

    class Operate(serializers.Serializer):
        id = serializers.CharField(required=True, label=_('folder id'))
        workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
        source = serializers.CharField(required=True, label=_('source'))

        @transaction.atomic
        def edit(self, instance):
            self.is_valid(raise_exception=True)
            Folder = get_folder_type(self.data.get('source'))
            current_id = self.data.get('id')
            current_node = Folder.objects.get(id=current_id)
            if current_node is None:
                raise serializers.ValidationError(_('Folder does not exist'))

            edit_field_list = ['name']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}

            QuerySet(Folder).filter(id=current_id).update(**edit_dict)

            # 模块间的移动
            parent_id = instance.get('parent_id')
            if parent_id is not None and current_id != 'root':
                # Folder 不能超过3层
                current_depth = get_max_depth(current_node)
                check_depth(self.data.get('source'), parent_id, current_depth)
                parent = Folder.objects.get(id=parent_id)
                current_node.move_to(parent)

            return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            Folder = get_folder_type(self.data.get('source'))
            folder = QuerySet(Folder).filter(id=self.data.get('id')).first()
            return FolderSerializer(folder).data

        def delete(self):
            self.is_valid(raise_exception=True)
            if self.data.get('id') == 'root':
                raise serializers.ValidationError(_('Cannot delete root folder'))
            Folder = get_folder_type(self.data.get('source'))
            QuerySet(Folder).filter(id=self.data.get('id')).delete()


class FolderTreeSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
    source = serializers.CharField(required=True, label=_('source'))

    def get_folder_tree(self, name=None):
        self.is_valid(raise_exception=True)
        Folder = get_folder_type(self.data.get('source'))
        if name is not None:
            nodes = Folder.objects.filter(Q(workspace_id=self.data.get('workspace_id')) &
                                          Q(name__contains=name)).get_cached_trees()
        else:
            nodes = Folder.objects.filter(Q(workspace_id=self.data.get('workspace_id'))).get_cached_trees()
        TreeSerializer = get_folder_tree_serializer(self.data.get('source'))
        serializer = TreeSerializer(nodes, many=True)
        return serializer.data  # 这是可序列化的字典
