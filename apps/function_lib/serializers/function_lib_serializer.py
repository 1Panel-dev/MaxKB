# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib_serializer.py
    @date：2024/8/2 17:35
    @desc:
"""
import io
import json
import pickle
import re
import uuid

from django.core import validators
from django.db import transaction
from django.db.models import QuerySet, Q, OuterRef, Exists
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField, UploadedImageField
from common.response import result
from common.util.common import restricted_loads
from common.util.field_message import ErrMessage
from common.util.function_code import FunctionExecutor
from common.util.rsa_util import rsa_long_decrypt, rsa_long_encrypt
from dataset.models import File
from function_lib.models.function import FunctionLib, PermissionType, FunctionType
from smartdoc.const import CONFIG

function_executor = FunctionExecutor(CONFIG.get('SANDBOX'))

class FlibInstance:
    def __init__(self, function_lib: dict, version: str):
        self.function_lib = function_lib
        self.version = version

def encryption(message: str):
    """
        加密敏感字段数据  加密方式是 如果密码是 1234567890  那么给前端则是 123******890
    :param message:
    :return:
    """
    if type(message) != str:
        return message
    if message == "":
        return ""
    max_pre_len = 8
    max_post_len = 4
    message_len = len(message)
    pre_len = int(message_len / 5 * 2)
    post_len = int(message_len / 5 * 1)
    pre_str = "".join([message[index] for index in
                       range(0,
                             max_pre_len if pre_len > max_pre_len else 1 if pre_len <= 0 else int(
                                 pre_len))])
    end_str = "".join(
        [message[index] for index in
         range(message_len - (int(post_len) if pre_len < max_post_len else max_post_len),
               message_len)])
    content = "***************"
    return pre_str + content + end_str


class FunctionLibModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunctionLib
        fields = ['id', 'name', 'icon', 'desc', 'code', 'input_field_list','init_field_list', 'init_params', 'permission_type', 'is_active', 'user_id', 'template_id',
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
    init_field_list = serializers.ListField(required=False, default=list)
    init_params = serializers.JSONField(required=False, default=dict)
    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_('function content')))


class EditFunctionLib(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function name')))

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function description')))

    code = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function content')))

    input_field_list = FunctionLibInputField(required=False, many=True)

    init_field_list = serializers.ListField(required=False, default=list)

    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_('Is active')))


class CreateFunctionLib(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char(_('function name')))

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function description')))

    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_('function content')))

    input_field_list = FunctionLibInputField(required=True, many=True)

    init_field_list = serializers.ListField(required=False, default=list)

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
        function_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)


        def get_query_set(self):
            query_set = QuerySet(FunctionLib).filter(
                (Q(user_id=self.data.get('user_id')) | Q(permission_type='PUBLIC')))
            if self.data.get('name') is not None:
                query_set = query_set.filter(name__icontains=self.data.get('name'))
            if self.data.get('desc') is not None:
                query_set = query_set.filter(desc__contains=self.data.get('desc'))
            if self.data.get('is_active') is not None:
                query_set = query_set.filter(is_active=self.data.get('is_active'))
            if self.data.get('select_user_id') is not None:
                query_set = query_set.filter(user_id=self.data.get('select_user_id'))
            if self.data.get('function_type') is not None:
                query_set = query_set.filter(function_type=self.data.get('function_type'))
            query_set = query_set.order_by("-create_time")

            return query_set

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            rs = []
            for item in self.get_query_set():
                data = {**FunctionLibModelSerializer(item).data, 'init_params': None}
                rs.append(data)
            return rs

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)

            def post_records_handler(row):
                return {
                    **FunctionLibModelSerializer(row).data,
                    'init_params': None
                }

            return page_search(current_page, page_size, self.get_query_set(),
                               post_records_handler=post_records_handler)

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
                                       init_field_list=instance.get('init_field_list'),
                                       permission_type=instance.get('permission_type'),
                                       is_active=False)
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
            init_params = debug_instance.get('init_params')
            params = {field.get('name'): self.convert_value(field.get('name'), field.get('value'), field.get('type'),
                                                            field.get('is_required'))
                      for field in
                      [{'value': self.get_field_value(debug_field_list, field.get('name'), field.get('is_required')),
                        **field} for field in
                       input_field_list]}
            # 合并初始化参数
            if init_params is not None:
                all_params = init_params | params
            else:
                all_params = params
            return function_executor.exec_code(code, all_params)

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
            if not QuerySet(FunctionLib).filter(id=self.data.get('id')).exists():
                raise AppApiException(500, _('Function does not exist'))

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            fun = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            if fun.template_id is None and fun.icon != '/ui/favicon.ico':
                QuerySet(File).filter(id=fun.icon.split('/')[-1]).delete()
            QuerySet(FunctionLib).filter(id=self.data.get('id')).delete()
            return True

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                EditFunctionLib(data=instance).is_valid(raise_exception=True)
            edit_field_list = ['name', 'desc', 'code', 'icon', 'input_field_list', 'init_field_list', 'init_params', 'permission_type', 'is_active']
            edit_dict = {field: instance.get(field) for field in edit_field_list if (
                    field in instance and instance.get(field) is not None)}

            function_lib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            if 'init_params' in edit_dict:
                if edit_dict['init_field_list'] is not None:
                    rm_key = []
                    for key in edit_dict['init_params']:
                        if key not in [field['field'] for field in edit_dict['init_field_list']]:
                            rm_key.append(key)
                    for key in rm_key:
                        edit_dict['init_params'].pop(key)
                if function_lib.init_params:
                    old_init_params = json.loads(rsa_long_decrypt(function_lib.init_params))
                    for key in edit_dict['init_params']:
                        if key in old_init_params and edit_dict['init_params'][key] == encryption(old_init_params[key]):
                            edit_dict['init_params'][key] = old_init_params[key]
                edit_dict['init_params'] = rsa_long_encrypt(json.dumps(edit_dict['init_params']))
            QuerySet(FunctionLib).filter(id=self.data.get('id')).update(**edit_dict)
            return self.one(False)

        def one(self, with_valid=True):
            if with_valid:
                super().is_valid(raise_exception=True)
                if not QuerySet(FunctionLib).filter(id=self.data.get('id')).filter(
                        Q(user_id=self.data.get('user_id')) | Q(permission_type='PUBLIC')).exists():
                    raise AppApiException(500, _('Function does not exist'))
            function_lib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            if function_lib.init_params:
                function_lib.init_params = json.loads(rsa_long_decrypt(function_lib.init_params))
            if function_lib.init_field_list:
                password_fields = [i["field"] for i in function_lib.init_field_list if i.get("input_type") == "PasswordInput"]
                if function_lib.init_params:
                    for k in function_lib.init_params:
                        if k in password_fields and function_lib.init_params[k]:
                            function_lib.init_params[k] = encryption(function_lib.init_params[k])
            return {**FunctionLibModelSerializer(function_lib).data, 'init_params': function_lib.init_params}

        def export(self, with_valid=True):
            try:
                if with_valid:
                    self.is_valid()
                id = self.data.get('id')
                function_lib = QuerySet(FunctionLib).filter(id=id).first()
                application_dict = FunctionLibModelSerializer(function_lib).data
                mk_instance = FlibInstance(application_dict, 'v1')
                application_pickle = pickle.dumps(mk_instance)
                response = HttpResponse(content_type='text/plain', content=application_pickle)
                response['Content-Disposition'] = f'attachment; filename="{function_lib.name}.fx"'
                return response
            except Exception as e:
                return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class Import(serializers.Serializer):
        file = UploadedFileField(required=True, error_messages=ErrMessage.image(_("file")))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("User ID")))

        @transaction.atomic
        def import_(self, with_valid=True):
            if with_valid:
                self.is_valid()
            user_id = self.data.get('user_id')
            flib_instance_bytes = self.data.get('file').read()
            try:
                flib_instance = restricted_loads(flib_instance_bytes)
            except Exception as e:
                raise AppApiException(1001, _("Unsupported file format"))
            function_lib = flib_instance.function_lib
            function_lib_model = FunctionLib(id=uuid.uuid1(), name=function_lib.get('name'),
                                             desc=function_lib.get('desc'),
                                             code=function_lib.get('code'),
                                             user_id=user_id,
                                             input_field_list=function_lib.get('input_field_list'),
                                             init_field_list=function_lib.get('init_field_list', []),
                                             permission_type='PRIVATE',
                                             is_active=False)
            function_lib_model.save()
            return True

    class IconOperate(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("function ID")))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("User ID")))
        image = UploadedImageField(required=True, error_messages=ErrMessage.image(_("picture")))

        def edit(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            functionLib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            if functionLib is None:
                raise AppApiException(500, _('Function does not exist'))
            # 删除旧的图片
            if functionLib.icon != '/ui/favicon.ico':
                QuerySet(File).filter(id=functionLib.icon.split('/')[-1]).delete()
            if self.data.get('image') is None:
                functionLib.icon = '/ui/favicon.ico'
            else:
                meta = {
                    'debug': False
                }
                file_id = uuid.uuid1()
                file = File(id=file_id, file_name=self.data.get('image').name, meta=meta)
                file.save(self.data.get('image').read())

                functionLib.icon = f'/api/file/{file_id}'
            functionLib.save()

            return functionLib.icon

    class InternalFunction(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("function ID")))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("User ID")))
        name = serializers.CharField(required=True, error_messages=ErrMessage.char(_("function name")))

        def add(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)

            internal_function_lib = QuerySet(FunctionLib).filter(id=self.data.get('id')).first()
            if internal_function_lib is None:
                raise AppApiException(500, _('Function does not exist'))

            function_lib = FunctionLib(
                id=uuid.uuid1(),
                name=self.data.get('name'),
                desc=internal_function_lib.desc,
                code=internal_function_lib.code,
                user_id=self.data.get('user_id'),
                input_field_list=internal_function_lib.input_field_list,
                init_field_list=internal_function_lib.init_field_list,
                permission_type=PermissionType.PRIVATE,
                template_id=internal_function_lib.id,
                function_type=FunctionType.PUBLIC,
                icon=internal_function_lib.icon,
                is_active=False
            )
            function_lib.save()

            return FunctionLibModelSerializer(function_lib).data
