# -*- coding: utf-8 -*-
import io
import json
import os
import pickle
import re

import uuid_utils.compat as uuid
from django.core import validators
from django.db import transaction
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from pylint.lint import Run
from pylint.reporters import JSON2Reporter
from rest_framework import serializers, status

from common.db.search import page_search, native_page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedImageField
from common.result import result
from common.utils.common import get_file_content
from common.utils.rsa_util import rsa_long_decrypt, rsa_long_encrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models import File, FileSourceType
from maxkb.const import CONFIG, PROJECT_DIR
from tools.models import Tool, ToolScope, ToolFolder
from tools.serializers.tool_folder import ToolFolderFlatSerializer

tool_executor = ToolExecutor(CONFIG.get('SANDBOX'))


class ToolInstance:
    def __init__(self, tool: dict, version: str):
        self.tool = tool
        self.version = version


ALLOWED_CLASSES = {
    ("builtins", "dict"),
    ('uuid', 'UUID'),
    ("tools.serializers.tool", "ToolInstance")
}


def to_dict(message, file_name):
    return {
        'line': message.line,
        'column': message.column,
        'endLine': message.end_line,
        'endColumn': message.end_column,
        'message': (message.msg or "").replace(file_name, 'code'),
        'type': message.category
    }


def get_file_name():
    file_name = f"{uuid.uuid7()}"
    pylint_dir = os.path.join(PROJECT_DIR, 'data', 'pylint')
    if not os.path.exists(pylint_dir):
        os.makedirs(pylint_dir)
    return os.path.join(pylint_dir, file_name)


class RestrictedUnpickler(pickle.Unpickler):

    def find_class(self, folder, name):
        if (folder, name) in ALLOWED_CLASSES:
            return super().find_class(folder, name)
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (folder, name))


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


class ToolModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'icon', 'desc', 'code', 'input_field_list', 'init_field_list', 'init_params',
                  'scope', 'is_active', 'user_id', 'template_id', 'workspace_id', 'folder_id',
                  'create_time', 'update_time']


class UploadedFileField(serializers.FileField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, value):
        return value


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

    folder_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='root')


class ToolEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, label=_('tool name'))

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 label=_('tool description'))

    code = serializers.CharField(required=False, label=_('tool content'))

    input_field_list = serializers.ListField(child=ToolInputField(), required=False, default=list,
                                             label=_('input field list'))

    init_field_list = serializers.ListField(child=InitField(), required=False, default=list, label=_('init field list'))

    init_params = serializers.DictField(required=False, default=dict, label=_('init params'))

    is_active = serializers.BooleanField(required=False, label=_('Is active'))

    folder_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='root')


class DebugField(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('variable name'))
    value = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('variable value'))


class ToolDebugRequest(serializers.Serializer):
    code = serializers.CharField(required=True, label=_('tool content'))
    input_field_list = serializers.ListField(child=ToolInputField(), required=False, default=list,
                                             label=_('input field list'))
    init_field_list = serializers.ListField(child=InitField(), required=False, default=list, label=_('init field list'))
    init_params = serializers.DictField(required=False, default=dict, label=_('init params'))
    debug_field_list = DebugField(required=True, many=True)


class PylintInstance(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('function content'))


class ToolSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

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
                        scope=instance.get('scope', ToolScope.WORKSPACE),
                        folder_id=instance.get('folder_id', 'root'),
                        is_active=False)
            tool.save()
            return ToolModelSerializer(tool).data

    class Debug(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        def debug(self, debug_instance):
            self.is_valid(raise_exception=True)
            ToolDebugRequest(data=debug_instance).is_valid(raise_exception=True)
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
            return tool_executor.exec_code(code, all_params)

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

            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            if 'init_params' in edit_dict:
                if edit_dict['init_field_list'] is not None:
                    rm_key = []
                    for key in edit_dict['init_params']:
                        if key not in [field['field'] for field in edit_dict['init_field_list']]:
                            rm_key.append(key)
                    for key in rm_key:
                        edit_dict['init_params'].pop(key)
                if tool.init_params:
                    old_init_params = json.loads(rsa_long_decrypt(tool.init_params))
                    for key in edit_dict['init_params']:
                        if key in old_init_params and edit_dict['init_params'][key] == encryption(old_init_params[key]):
                            edit_dict['init_params'][key] = old_init_params[key]
                edit_dict['init_params'] = rsa_long_encrypt(json.dumps(edit_dict['init_params']))

            QuerySet(Tool).filter(id=self.data.get('id')).update(**edit_dict)

            return self.one()

        def delete(self):
            self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            if tool.template_id is None and tool.icon != '/ui/favicon.ico':
                QuerySet(File).filter(id=tool.icon.split('/')[-1]).delete()
            QuerySet(Tool).filter(id=self.data.get('id')).delete()

        def one(self):
            self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            if tool.init_params:
                tool.init_params = json.loads(rsa_long_decrypt(tool.init_params))
            if tool.init_field_list:
                password_fields = [i["field"] for i in tool.init_field_list if
                                   i.get("input_type") == "PasswordInput"]
                if tool.init_params:
                    for k in tool.init_params:
                        if k in password_fields and tool.init_params[k]:
                            tool.init_params[k] = encryption(tool.init_params[k])
            return ToolModelSerializer(tool).data

        def export(self):
            try:
                self.is_valid()
                id = self.data.get('id')
                tool = QuerySet(Tool).filter(id=id).first()
                tool_dict = ToolModelSerializer(tool).data
                mk_instance = ToolInstance(tool_dict, 'v2')
                tool_pickle = pickle.dumps(mk_instance)
                response = HttpResponse(content_type='text/plain', content=tool_pickle)
                response['Content-Disposition'] = f'attachment; filename="{tool.name}.fx"'
                return response
            except Exception as e:
                return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class Pylint(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        def run(self, instance, is_valid=True):
            if is_valid:
                self.is_valid(raise_exception=True)
                PylintInstance(data=instance).is_valid(raise_exception=True)
            code = instance.get('code')
            file_name = get_file_name()
            with open(file_name, 'w') as file:
                file.write(code)
            reporter = JSON2Reporter()
            Run([file_name,
                 "--disable=line-too-long",
                 '--module-rgx=[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'],
                reporter=reporter, exit=False)
            os.remove(file_name)
            return [to_dict(m, os.path.basename(file_name)) for m in reporter.messages]

    class Import(serializers.Serializer):
        file = UploadedFileField(required=True, label=_("file"))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))

        #
        @transaction.atomic
        def import_(self, scope=ToolScope.WORKSPACE):
            self.is_valid()

            user_id = self.data.get('user_id')
            tool_instance_bytes = self.data.get('file').read()
            try:
                tool_instance = RestrictedUnpickler(io.BytesIO(tool_instance_bytes)).load()
            except Exception as e:
                raise AppApiException(1001, _("Unsupported file format"))
            tool = tool_instance.tool
            tool_model = Tool(
                id=uuid.uuid7(),
                name=tool.get('name'),
                desc=tool.get('desc'),
                code=tool.get('code'),
                user_id=user_id,
                input_field_list=tool.get('input_field_list'),
                init_field_list=tool.get('init_field_list', []),
                scope=scope,
                is_active=False
            )
            tool_model.save()
            return True

    class IconOperate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_("function ID"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        image = UploadedImageField(required=True, label=_("picture"))

        def edit(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            if tool is None:
                raise AppApiException(500, _('Function does not exist'))
            # 删除旧的图片
            if tool.icon != '/ui/favicon.ico':
                QuerySet(File).filter(id=tool.icon.split('/')[-1]).delete()
            if self.data.get('image') is None:
                tool.icon = '/ui/favicon.ico'
            else:
                meta = {
                    'debug': False
                }
                file_id = uuid.uuid7()
                file = File(
                    id=file_id,
                    file_name=self.data.get('image').name,
                    source_type=FileSourceType.TOOL,
                    source_id=tool.id,
                    meta=meta
                )
                file.save(self.data.get('image').read())

                tool.icon = f'/oss/file/{file_id}'
            tool.save()

            return tool.icon


class ToolTreeSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def get_tools(self, folder_id):
        self.is_valid(raise_exception=True)
        if not folder_id:
            folder_id = 'root'
        # 获取当前文件夹
        current_folder = ToolFolder.objects.filter(id=folder_id).first()
        if not current_folder:
            raise serializers.ValidationError(_('Folder not found'))

        # 获取当前文件夹下的直接子文件夹
        child_folders = ToolFolder.objects.filter(parent=current_folder)
        folders_data = ToolFolderFlatSerializer(child_folders, many=True).data

        # 获取当前文件夹下的工具
        tools = QuerySet(Tool).filter(Q(workspace_id=self.data.get('workspace_id')) &
                                      Q(folder_id=folder_id))
        tools_data = ToolModelSerializer(tools, many=True).data

        # 返回包含文件夹和工具的结构
        return {
            'folders': folders_data,
            'tools': tools_data,
        }

    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        folder_id = serializers.CharField(required=True, label=_('folder id'))
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('tool name'))
        user_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('user id'))
        scope = serializers.CharField(required=True, label=_('scope'))

        def page_tool(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)

            folder_id = self.data.get('folder_id', 'root')
            root = ToolFolder.objects.filter(id=folder_id).first()
            if not root:
                raise serializers.ValidationError(_('Folder not found'))
            # 使用MPTT的get_descendants()方法获取所有相关节点
            all_folders = root.get_descendants(include_self=True)

            if self.data.get('name'):
                tools = QuerySet(Tool).filter(
                    Q(workspace_id=self.data.get('workspace_id')) &
                    Q(folder_id__in=all_folders) &
                    Q(user_id=self.data.get('user_id')) &
                    Q(name__contains=self.data.get('name'))
                )
            else:
                tools = QuerySet(Tool).filter(
                    Q(workspace_id=self.data.get('workspace_id')) &
                    Q(folder_id__in=all_folders) &
                    Q(user_id=self.data.get('user_id'))
                )
            return page_search(current_page, page_size, tools, lambda record: ToolModelSerializer(record).data)

        def get_query_set(self):
            tool_query_set = QuerySet(Tool)
            tool_scope_query_set = QuerySet(Tool)
            folder_query_set = QuerySet(ToolFolder)
            workspace_id = self.data.get('workspace_id')
            user_id = self.data.get('user_id')
            scope = self.data.get('scope')
            desc = self.data.get('desc')
            name = self.data.get('name')
            folder_id = self.data.get('folder_id')

            if workspace_id is not None:
                folder_query_set = folder_query_set.filter(workspace_id=workspace_id)
                tool_query_set = tool_query_set.filter(workspace_id=workspace_id)
            if user_id is not None:
                folder_query_set = folder_query_set.filter(user_id=user_id)
                tool_query_set = tool_query_set.filter(user_id=user_id)
            if folder_id is not None:
                folder_query_set = folder_query_set.filter(parent=folder_id)
                tool_query_set = tool_query_set.filter(folder_id=folder_id)
            if name is not None:
                folder_query_set = folder_query_set.filter(name__contains=name)
                tool_query_set = tool_query_set.filter(name__contains=name)
            if desc is not None:
                folder_query_set = folder_query_set.filter(desc__contains=desc)
                tool_query_set = tool_query_set.filter(desc__contains=desc)
            tool_query_set = tool_query_set.order_by("-update_time")

            if scope is not None:
                tool_scope_query_set = tool_scope_query_set.filter(scope=scope)

            return {
                'folder_query_set': folder_query_set,
                'tool_query_set': tool_query_set,
                'tool_scope_query_set': tool_scope_query_set
            }

        def page_tool_with_folders(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)

            return native_page_search(
                current_page, page_size, self.get_query_set(),
                get_file_content(os.path.join(PROJECT_DIR, "apps", "tools", 'sql', 'list_tool.sql'))
            )
