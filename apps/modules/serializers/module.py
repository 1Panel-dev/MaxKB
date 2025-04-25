# -*- coding: utf-8 -*-

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet, Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.permission_constants import Group
from knowledge.models import KnowledgeModule
from modules.api.module import ModuleCreateRequest
from tools.models import ToolModule
from tools.serializers.tool_module import ToolModuleTreeSerializer


def get_module_type(source):
    if source == Group.TOOL.name:
        return ToolModule
    elif source == Group.APPLICATION.name:
        # todo app module
        return None
    elif source == Group.KNOWLEDGE.name:
        return KnowledgeModule
    else:
        return None


MODULE_DEPTH = 3  # Module 不能超过3层


def check_depth(source, parent_id):
    # Module 不能超过3层
    Module = get_module_type(source)

    if parent_id != 'root':
        # 计算当前层级
        depth = 1  # 当前要创建的节点算一层
        current_parent_id = parent_id

        # 向上追溯父节点
        while current_parent_id != 'root':
            depth += 1
            parent_node = QuerySet(Module).filter(id=current_parent_id).first()
            if parent_node is None:
                break
            current_parent_id = parent_node.parent_id

        # 验证层级深度
        if depth > MODULE_DEPTH:
            raise serializers.ValidationError(_('Module depth cannot exceed 3 levels'))


class ModuleSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_('module id'))
    name = serializers.CharField(required=True, label=_('module name'))
    user_id = serializers.CharField(required=True, label=_('module user id'))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('workspace id'))
    parent_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('parent id'))

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        source = serializers.CharField(required=True, label=_('source'))

        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ModuleCreateRequest(data=instance).is_valid(raise_exception=True)

            workspace_id = self.data.get('workspace_id', 'default')
            parent_id = instance.get('parent_id', 'root')
            name = instance.get('name')

            Module = get_module_type(self.data.get('source'))
            if QuerySet(Module).filter(name=name, workspace_id=workspace_id, parent_id=parent_id).exists():
                raise serializers.ValidationError(_('Module name already exists'))
            # Module 不能超过3层
            check_depth(self.data.get('source'), parent_id)

            module = Module(
                id=uuid.uuid7(),
                name=instance.get('name'),
                user_id=self.data.get('user_id'),
                workspace_id=workspace_id,
                parent_id=parent_id
            )
            module.save()
            return ModuleSerializer(module).data

    class Operate(serializers.Serializer):
        id = serializers.CharField(required=True, label=_('module id'))
        workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
        source = serializers.CharField(required=True, label=_('source'))

        @transaction.atomic
        def edit(self, instance):
            self.is_valid(raise_exception=True)
            Module = get_module_type(self.data.get('source'))
            current_id = self.data.get('id')
            current_node = Module.objects.get(id=current_id)
            if current_node is None:
                raise serializers.ValidationError(_('Module does not exist'))

            edit_field_list = ['name']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}

            QuerySet(Module).filter(id=current_id).update(**edit_dict)

            # 模块间的移动
            parent_id = instance.get('parent_id')
            if parent_id is not None and current_id != 'root':
                # Module 不能超过3层
                check_depth(self.data.get('source'), parent_id)
                parent = Module.objects.get(id=parent_id)
                current_node.move_to(parent)

            return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            Module = get_module_type(self.data.get('source'))
            module = QuerySet(Module).filter(id=self.data.get('id')).first()
            return ModuleSerializer(module).data

        def delete(self):
            self.is_valid(raise_exception=True)
            if self.data.get('id') == 'root':
                raise serializers.ValidationError(_('Cannot delete root module'))
            Module = get_module_type(self.data.get('source'))
            QuerySet(Module).filter(id=self.data.get('id')).delete()


class ModuleTreeSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
    source = serializers.CharField(required=True, label=_('source'))

    def get_module_tree(self, name=None):
        self.is_valid(raise_exception=True)
        Module = get_module_type(self.data.get('source'))
        if name is not None:
            nodes = Module.objects.filter(Q(workspace_id=self.data.get('workspace_id')) &
                                          Q(name__contains=name)).get_cached_trees()
        else:
            nodes = Module.objects.filter(Q(workspace_id=self.data.get('workspace_id'))).get_cached_trees()
        serializer = ToolModuleTreeSerializer(nodes, many=True)
        return serializer.data  # 这是可序列化的字典
