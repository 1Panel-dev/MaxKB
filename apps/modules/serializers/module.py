# -*- coding: utf-8 -*-

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.constants.permission_constants import Group
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
        # todo knowledge module
        return None
    else:
        return None


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

        def edit(self, instance):
            self.is_valid(raise_exception=True)
            Module = get_module_type(self.data.get('source'))
            if not QuerySet(Module).filter(id=self.data.get('id')).exists():
                raise serializers.ValidationError(_('Module does not exist'))

            edit_field_list = ['name']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}

            QuerySet(Module).filter(id=self.data.get('id')).update(**edit_dict)

            return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            Module = get_module_type(self.data.get('source'))
            module = QuerySet(Module).filter(id=self.data.get('id')).first()
            return ModuleSerializer(module).data


class ModuleTreeSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('workspace id'))
    source = serializers.CharField(required=True, label=_('source'))

    def get_module_tree(self):
        self.is_valid(raise_exception=True)
        Module = get_module_type(self.data.get('source'))
        nodes = Module.objects.filter(workspace_id=self.data.get('workspace_id')).get_cached_trees()
        serializer = ToolModuleTreeSerializer(nodes, many=True)
        return serializer.data  # 这是可序列化的字典
