# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib_serializer.py
    @date：2024/8/2 17:35
    @desc:
"""
import json
import re
import uuid

from django.core import validators
from django.db.models import QuerySet, Q
from rest_framework import serializers

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage
from common.util.function_code import FunctionExecutor
from function_lib.models.function import FunctionLib
from smartdoc.const import CONFIG
from django.utils.translation import gettext_lazy as _

function_executor = FunctionExecutor(CONFIG.get('SANDBOX'))


class FunctionLibModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionLib
        fields = ['id', 'name', 'desc', 'code', 'input_field_list', 'permission_type', 'is_active', 'user_id',
                  'create_time', 'update_time']


class FunctionLibInputField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char(_('variable name')))
    is_required = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean(_('required')))
    type = serializers.CharField(required=True, error_messages=ErrMessage.char(_('type')), validators=[
        validators.RegexValidator(regex=re.compile("^string|int|dict|array|float$"),
                                  message=_('fields only support string|int|dict|array|float'), code=500)
    ])
    source = serializers.CharField(required=True, error_messages=ErrMessage.char(_('source')), validators=[
        validators.RegexValidator(regex=re.compile("^custom|reference$"),
                                  message=_('The field only supports custom|reference'), code=500)
    ])


class DebugField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char(_('variable name')))
    value = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                  error_messages=ErrMessage.char(_('variable value')))


class DebugInstance(serializers.Serializer):
    debug_field_list = DebugField(required=True, many=True)
    input_field_list = FunctionLibInputField(required=True, many=True)
    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_('function content')))


class EditFunctionLib(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function name')))

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function description')))

    code = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function content')))

    input_field_list = FunctionLibInputField(required=False, many=True)

    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_('Is active')))


class CreateFunctionLib(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char(_('function name')))

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function description')))

    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_('function content')))

    input_field_list = FunctionLibInputField(required=True, many=True)

    permission_type = serializers.CharField(required=True, error_messages=ErrMessage.char(_('permission')), validators=[
        validators.RegexValidator(regex=re.compile("^PUBLIC|PRIVATE$"),
                                  message="权限只支持PUBLIC|PRIVATE", code=500)
    ])
    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_('Is active')))


class FunctionLibSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char(_('function name')))

        desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char(_('function description')))
        is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_('Is active')))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('user id')))
        select_user_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

        def get_query_set(self):
            query_set = QuerySet(FunctionLib).filter(
                (Q(user_id=self.data.get('user_id')) | Q(permission_type='PUBLIC')))
            if self.data.get('name') is not None:
                query_set = query_set.filter(name__contains=self.data.get('name'))
            if self.data.get('desc') is not None:
                query_set = query_set.filter(desc__contains=self.data.get('desc'))
            if self.data.get('is_active') is not None:
                query_set = query_set.filter(is_active=self.data.get('is_active'))
            if self.data.get('select_user_id') is not None:
                query_set = query_set.filter(user_id=self.data.get('select_user_id'))
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [FunctionLibModelSerializer(item).data for item in self.get_query_set()]

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(current_page, page_size, self.get_query_set(),
                               post_records_handler=lambda row: FunctionLibModelSerializer(row).data)

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('user id')))

        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                CreateFunctionLib(data=instance).is_valid(raise_exception=True)
            function_lib = FunctionLib(id=uuid.uuid1(), name=instance.get('name'), desc=instance.get('desc'),
                                       code=instance.get('code'),
                                       user_id=self.data.get('user_id'),
                                       input_field_list=instance.get('input_field_list'),
                                       permission_type=instance.get('permission_type'),
                                       is_active=instance.get('is_active', True))
            function_lib.save()
            return FunctionLibModelSerializer(function_lib).data

    class Debug(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('user id')))

        def debug(self, debug_instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                DebugInstance(data=debug_instance).is_valid(raise_exception=True)
            input_field_list = debug_instance.get('input_field_list')
            code = debug_instance.get('code')
            debug_field_list = debug_instance.get('debug_field_list')
            params = {field.get('name'): self.convert_value(field.get('name'), field.get('value'), field.get('type'),
                                                            field.get('is_required'))
                      for field in
                      [{'value': self.get_field_value(debug_field_list, field.get('name'), field.get('is_required')),
                        **field} for field in
                       input_field_list]}
            return function_executor.exec_code(code, params)

        @staticmethod
        def get_field_value(debug_field_list, name, is_required):
            result = [field for field in debug_field_list if field.get('name') == name]
            if len(result) > 0:
                return result[-1].get('value')
            if is_required:
                raise AppApiException(500, f"{name}" + _('field has no value set'))
            return None

        @staticmethod
        def convert_value(name: str, value: str, _type: str, is_required: bool):
            if not is_required and value is None:
                return None
            try:
                if _type == 'int':
                    return int(value)
                if _type == 'float':
                    return float(value)
                if _type == 'dict':
                    v = json.loads(value)
                    if isinstance(v, dict):
                        return v
                    raise Exception(_('type error'))
                if _type == 'array':
                    v = json.loads(value)
                    if isinstance(v, list):
                        return v
                    raise Exception(_('type error'))
                return value
            except Exception as e:
                raise AppApiException(500, _('Field: {name} Type: {_type} Value: {value} Type conversion error').format(
                    name=name, type=_type, value=value
                ))

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('function id')))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('user id')))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(FunctionLib).filter(id=self.data.get('id'), user_id=self.data.get('user_id')).exists():
                raise AppApiException(500, _('Function does not exist'))

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(FunctionLib).filter(id=self.data.get('id')).delete()
            return True

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                EditFunctionLib(data=instance).is_valid(raise_exception=True)
            edit_field_list = ['name', 'desc', 'code', 'input_field_list', 'permission_type', 'is_active']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}
            QuerySet(FunctionLib).filter(id=self.data.get('id')).update(**edit_dict)
            return self.one(False)

        def one(self, with_valid=True):
            if with_valid:
                super().is_valid(raise_exception=True)
                if not QuerySet(FunctionLib).filter(id=self.data.get('id')).filter(
                        Q(user_id=self.data.get('user_id')) | Q(permission_type='PUBLIC')).exists():
                    raise AppApiException(500, _('Function does not exist'))
            function_lib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            return FunctionLibModelSerializer(function_lib).data
