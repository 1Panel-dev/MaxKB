# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib_serializer.py
    @date：2024/8/2 17:35
    @desc:
"""
import uuid

from django.db.models import QuerySet
from rest_framework import serializers

from common.db.search import page_search
from common.util.field_message import ErrMessage
from common.util.function_code import exec_code
from function_lib.models.function import FunctionLib


class FunctionLibModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionLib
        fields = ['id', 'name', 'desc', 'code', 'input_field_list',
                  'create_time', 'update_time']


class FunctionLibInputField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char('变量名'))
    is_required = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("是否必填"))
    type = serializers.CharField(required=True, error_messages=ErrMessage.char("类型"))
    source = serializers.CharField(required=True, error_messages=ErrMessage.char("来源"))


class DebugField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char('变量名'))
    value = serializers.CharField(required=True, error_messages=ErrMessage.char("变量值"))


class EditFunctionLib(serializers.Serializer):
    name = serializers.CharField(required=False, error_messages=ErrMessage.char("函数名称"))

    desc = serializers.CharField(required=False, error_messages=ErrMessage.char("函数描述"))

    code = serializers.CharField(required=False, error_messages=ErrMessage.char("函数内容"))

    input_field_list = FunctionLibInputField(required=False, many=True)


class FunctionLibSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        name = serializers.CharField(required=False, error_messages=ErrMessage.char("函数名称"))

        desc = serializers.CharField(required=False, error_messages=ErrMessage.char("函数描述"))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        def get_query_set(self):
            query_set = QuerySet(FunctionLib)
            if self.data.get('name') is not None:
                query_set = query_set.filter(name=self.data.get('name'))
            if self.data.get('desc') is not None:
                query_set = query_set.filter(name=self.data.get('desc'))
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
        name = serializers.CharField(required=True, error_messages=ErrMessage.char("函数名称"))

        desc = serializers.CharField(required=False, error_messages=ErrMessage.char("函数描述"))

        code = serializers.CharField(required=True, error_messages=ErrMessage.char("函数内容"))

        input_field_list = FunctionLibInputField(required=True, many=True)

        def insert(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            function_lib = FunctionLib(id=uuid.uuid1(), name=self.data.get('name'), desc=self.data.get('desc'),
                                       code=self.data.get('code'),
                                       input_field_list=self.data.get('input_field_list'))
            function_lib.save()
            return FunctionLibModelSerializer(function_lib).data

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("函数id"))

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                EditFunctionLib(data=instance).is_valid(raise_exception=True)
            edit_field_list = ['name', 'desc', 'code', 'input_field_list']
            edit_dict = {field: instance.get(field) for field in edit_field_list if
                         field in instance and instance.get('field') is not None}
            QuerySet(FunctionLib).filter(id=self.data.get('id')).update(**edit_dict)
            return self.one(False)

        def debug(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            function_lib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            exec_code(function_lib.code, self.input_field_list_to_params(function_lib.input_field_list))

        @staticmethod
        def input_field_list_to_params(input_field_list):
            return {field.get('name'): field.get('value') for field in input_field_list}

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            function_lib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            return FunctionLibModelSerializer(function_lib).data
