# -*- coding: utf-8 -*-
import re

import uuid_utils.compat as uuid
from django.core import validators
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from tools.models import Tool, ToolScope


class ToolModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'icon', 'desc', 'code', 'input_field_list', 'init_field_list', 'init_params',
                  'scope', 'is_active', 'user_id', 'template_id', 'workspace_id', 'module_id',
                  'create_time', 'update_time']


class ToolInputField(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('variable name'))
    is_required = serializers.BooleanField(required=True, label=_('required'))
    type = serializers.CharField(required=True, label=_('type'), validators=[
        validators.RegexValidator(regex=re.compile("^string|int|dict|array|float$"),
                                  message=_('fields only support string|int|dict|array|float'), code=500)
    ])
    source = serializers.CharField(required=True, label=_('source'), validators=[
        validators.RegexValidator(regex=re.compile("^custom|reference$"),
                                  message=_('The field only supports custom|reference'), code=500)
    ])


class InitField(serializers.Serializer):
    field = serializers.CharField(required=True, label=_('field name'))
    label = serializers.CharField(required=True, label=_('field label'))
    required = serializers.BooleanField(required=True, label=_('required'))
    input_type = serializers.CharField(required=True, label=_('input type'))
    default_value = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    show_default_value = serializers.BooleanField(required=False, default=False)
    props_info = serializers.DictField(required=False, default=dict)
    attrs = serializers.DictField(required=False, default=dict)


class ToolCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('tool name'))

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 label=_('tool description'))

    code = serializers.CharField(required=True, label=_('tool content'))

    input_field_list = serializers.ListField(child=ToolInputField(), required=False, default=list,
                                             label=_('input field list'))

    init_field_list = serializers.ListField(child=InitField(), required=False, default=list, label=_('init field list'))

    is_active = serializers.BooleanField(required=False, label=_('Is active'))

    module_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='root')


class ToolSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.UUIDField(required=True, label=_('workspace id'))

        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ToolCreateRequest(data=instance).is_valid(raise_exception=True)
            tool = Tool(id=uuid.uuid7(),
                        name=instance.get('name'),
                        desc=instance.get('desc'),
                        code=instance.get('code'),
                        user_id=self.data.get('user_id'),
                        input_field_list=instance.get('input_field_list', []),
                        init_field_list=instance.get('init_field_list', []),
                        scope=ToolScope.WORKSPACE,
                        is_active=False)
            tool.save()
            return ToolModelSerializer(tool).data

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_('tool id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ToolCreateRequest(data=instance).is_valid(raise_exception=True)
            if not QuerySet(Tool).filter(id=self.data.get('id')).exists():
                raise serializers.ValidationError(_('Tool not found'))

            edit_field_list = ['name', 'desc', 'code', 'icon', 'input_field_list', 'init_field_list', 'init_params',
                               'is_active']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}

            QuerySet(Tool).filter(id=self.data.get('id')).update(**edit_dict)

            return self.one()

        def delete(self):
            self.is_valid(raise_exception=True)
            QuerySet(Tool).filter(id=self.data.get('id')).delete()

        def one(self):
            self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            return ToolModelSerializer(tool).data
