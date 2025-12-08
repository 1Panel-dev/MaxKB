# -*- coding: utf-8 -*-
import asyncio
import io
import json
import os
import pickle
import re
import tempfile
import zipfile
from typing import Dict

import requests
import uuid_utils.compat as uuid
from django.core import validators
from django.db import transaction
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from langchain_mcp_adapters.client import MultiServerMCPClient
from pylint.lint import Run
from pylint.reporters import JSON2Reporter
from rest_framework import serializers, status

from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import page_search, native_page_search, native_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedImageField
from common.result import result
from common.utils.common import get_file_content
from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt, rsa_long_encrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models import File, FileSourceType
from maxkb.const import CONFIG, PROJECT_DIR
from system_manage.models import AuthTargetType, WorkspaceUserResourcePermission
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope, ToolFolder, ToolType
from users.serializers.user import is_workspace_manage

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
        os.makedirs(pylint_dir, 0o700, exist_ok=True)
        os.chmod(os.path.dirname(pylint_dir), 0o700)
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


def validate_mcp_config(servers: Dict):
    async def validate():
        client = MultiServerMCPClient(servers)
        await client.get_tools()

    try:
        asyncio.run(validate())
    except Exception as e:
        maxkb_logger.error(f"validate mcp config error: {e}, servers: {servers}")
        raise serializers.ValidationError(_('MCP configuration is invalid'))


class ToolModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'icon', 'desc', 'code', 'input_field_list', 'init_field_list', 'init_params',
                  'scope', 'is_active', 'user_id', 'template_id', 'workspace_id', 'folder_id', 'tool_type', 'label',
                  'version', 'create_time', 'update_time']


class ToolExportModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'icon', 'desc', 'code', 'input_field_list', 'init_field_list',
                  'scope', 'is_active', 'user_id', 'template_id', 'workspace_id', 'folder_id', 'tool_type', 'label',
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

    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('tool description'))

    code = serializers.CharField(required=True, label=_('tool content'))

    input_field_list = serializers.ListField(required=False, default=list, label=_('input field list'))

    init_field_list = serializers.ListField(required=False, default=list, label=_('init field list'))

    is_active = serializers.BooleanField(required=False, label=_('Is active'))

    folder_id = serializers.CharField(required=False, allow_null=True)


class ToolEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, label=_('tool name'), allow_null=True)
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('tool description'))
    code = serializers.CharField(required=False, label=_('tool content'), allow_null=True, )
    input_field_list = serializers.ListField(required=False, default=list, allow_null=True, label=_('input field list'))
    init_field_list = serializers.ListField(required=False, default=list, allow_null=True, label=_('init field list'))
    init_params = serializers.DictField(required=False, default=dict, allow_null=True, label=_('init params'))
    is_active = serializers.BooleanField(required=False, label=_('Is active'), allow_null=True, )
    folder_id = serializers.CharField(required=False, allow_null=True)


class AddInternalToolRequest(serializers.Serializer):
    name = serializers.CharField(required=False, label=_("tool name"), allow_null=True, allow_blank=True)
    folder_id = serializers.CharField(required=False, allow_null=True, label=_("folder id"))


class DebugField(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('variable name'))
    value = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('variable value'))


class ToolDebugRequest(serializers.Serializer):
    code = serializers.CharField(required=True, label=_('tool content'))
    input_field_list = serializers.ListField(required=False, default=list, label=_('input field list'))
    init_field_list = serializers.ListField(required=False, default=list, label=_('init field list'))
    init_params = serializers.DictField(required=False, default=dict, label=_('init params'))
    debug_field_list = DebugField(required=True, many=True)


class PylintInstance(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('function content'))


class ToolSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        folder_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('folder id'))
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('tool name'))
        user_id = serializers.UUIDField(required=False, allow_null=True, label=_('user id'))
        scope = serializers.CharField(required=True, label=_('scope'))
        tool_type = serializers.CharField(required=False, label=_('tool type'), allow_null=True, allow_blank=True)
        create_user = serializers.UUIDField(required=False, label=_('create user'), allow_null=True)

        def get_query_set(self, workspace_manage, is_x_pack_ee):
            tool_query_set = QuerySet(Tool).filter(workspace_id=self.data.get('workspace_id'))
            folder_query_set = QuerySet(ToolFolder)
            default_query_set = QuerySet(Tool)

            workspace_id = self.data.get('workspace_id')
            user_id = self.data.get('user_id')
            scope = self.data.get('scope')
            tool_type = self.data.get('tool_type')
            desc = self.data.get('desc')
            name = self.data.get('name')
            folder_id = self.data.get('folder_id')
            create_user = self.data.get('create_user')

            if workspace_id is not None:
                folder_query_set = folder_query_set.filter(workspace_id=workspace_id)
                default_query_set = default_query_set.filter(workspace_id=workspace_id)
            if folder_id is not None and folder_id != workspace_id:
                folder_query_set = folder_query_set.filter(parent=folder_id)
                default_query_set = default_query_set.filter(folder_id=folder_id)
            if name is not None:
                folder_query_set = folder_query_set.filter(name__icontains=name)
                default_query_set = default_query_set.filter(name__icontains=name)
            if desc is not None:
                folder_query_set = folder_query_set.filter(desc__icontains=desc)
                default_query_set = default_query_set.filter(desc__icontains=desc)
            if create_user is not None:
                tool_query_set = tool_query_set.filter(user_id=create_user)
                folder_query_set = folder_query_set.filter(user_id=create_user)

            default_query_set = default_query_set.order_by("-create_time")

            if scope is not None:
                tool_query_set = tool_query_set.filter(scope=scope)
            if tool_type:
                tool_query_set = tool_query_set.filter(tool_type=tool_type)

            query_set_dict = {
                'tool_query_set': tool_query_set,
                'default_query_set': default_query_set,
            }
            if not workspace_manage:
                query_set_dict['workspace_user_resource_permission_query_set'] = QuerySet(
                    WorkspaceUserResourcePermission).filter(
                    auth_target_type="TOOL",
                    workspace_id=workspace_id,
                    user_id=user_id
                )
            return query_set_dict

        def get_authorized_query_set(self):
            default_query_set = QuerySet(Tool)
            tool_type = self.data.get('tool_type')
            desc = self.data.get('desc')
            name = self.data.get('name')
            create_user = self.data.get('create_user')

            default_query_set = default_query_set.filter(workspace_id='None')
            default_query_set = default_query_set.filter(scope=ToolScope.SHARED)
            if name is not None:
                default_query_set = default_query_set.filter(name__icontains=name)
            if desc is not None:
                default_query_set = default_query_set.filter(desc__icontains=desc)
            if create_user is not None:
                default_query_set = default_query_set.filter(user_id=create_user)
            if tool_type:
                default_query_set = default_query_set.filter(tool_type=tool_type)

            default_query_set = default_query_set.order_by("-create_time")

            return default_query_set

        @staticmethod
        def is_x_pack_ee():
            workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
            role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
            return workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None

        def get_tools(self):
            self.is_valid(raise_exception=True)

            workspace_manage = is_workspace_manage(self.data.get('user_id'), self.data.get('workspace_id'))
            is_x_pack_ee = self.is_x_pack_ee()
            results = native_search(
                self.get_query_set(workspace_manage, is_x_pack_ee),
                get_file_content(
                    os.path.join(
                        PROJECT_DIR,
                        "apps", "tools", 'sql',
                        'list_tool.sql' if workspace_manage else (
                            'list_tool_user_ee.sql' if is_x_pack_ee else 'list_tool_user.sql'
                        )
                    )
                ),
            )

            get_authorized_tool = DatabaseModelManage.get_model("get_authorized_tool")
            shared_queryset = QuerySet(Tool).none()
            if get_authorized_tool is not None:
                shared_queryset = self.get_authorized_query_set()
                shared_queryset = get_authorized_tool(shared_queryset, self.data.get('workspace_id'))

            return {
                'shared_tools': [
                    ToolModelSerializer(data).data for data in shared_queryset
                ],
                'tools': [
                    {
                        **tool,
                        'input_field_list': json.loads(tool.get('input_field_list', '[]')),
                        'init_field_list': json.loads(tool.get('init_field_list', '[]')),
                    } for tool in results if tool['resource_type'] == 'tool'
                ],
            }

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        @transaction.atomic
        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ToolCreateRequest(data=instance).is_valid(raise_exception=True)
                # 校验代码是否包括禁止的关键字
                ToolExecutor().validate_banned_keywords(instance.get('code', ''))
                if instance.get('tool_type') == ToolType.MCP:
                    ToolExecutor().validate_mcp_transport(instance.get('code', ''))

            tool_id = uuid.uuid7()
            Tool(
                id=tool_id,
                name=instance.get('name'),
                desc=instance.get('desc'),
                code=instance.get('code'),
                user_id=self.data.get('user_id'),
                workspace_id=self.data.get('workspace_id'),
                input_field_list=instance.get('input_field_list', []),
                init_field_list=instance.get('init_field_list', []),
                scope=instance.get('scope', ToolScope.WORKSPACE),
                tool_type=instance.get('tool_type', ToolType.CUSTOM),
                folder_id=instance.get('folder_id', self.data.get('workspace_id')),
                is_active=False
            ).save()

            # 自动授权给创建者
            UserResourcePermissionSerializer(data={
                'workspace_id': self.data.get('workspace_id'),
                'user_id': self.data.get('user_id'),
                'auth_target_type': AuthTargetType.TOOL.value
            }).auth_resource(str(tool_id))
            return ToolSerializer.Operate(data={
                'id': tool_id, 'workspace_id': self.data.get('workspace_id')
            }).one()

    class TestConnection(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        code = serializers.CharField(required=True, label=_('tool content'))

        def test_connection(self):
            self.is_valid(raise_exception=True)
            # 校验代码是否包括禁止的关键字
            ToolExecutor().validate_banned_keywords(self.data.get('code', ''))
            ToolExecutor().validate_mcp_transport(self.data.get('code', ''))

            # 校验mcp json
            validate_mcp_config(json.loads(self.data.get('code')))
            return True

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

        def is_one_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Tool).filter(id=self.data.get('id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                get_authorized_tool = DatabaseModelManage.get_model('get_authorized_tool')
                if get_authorized_tool:
                    if not get_authorized_tool(QuerySet(Tool).filter(id=self.data.get('id')), workspace_id).exists():
                        raise AppApiException(500, _('Tool id does not exist'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Tool).filter(id=self.data.get('id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Tool id does not exist'))

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ToolEditRequest(data=instance).is_valid(raise_exception=True)
                # 校验代码是否包括禁止的关键字
                ToolExecutor().validate_banned_keywords(instance.get('code', ''))
                if instance.get('tool_type') == ToolType.MCP:
                    ToolExecutor().validate_mcp_transport(instance.get('code', ''))

            if not QuerySet(Tool).filter(id=self.data.get('id')).exists():
                raise serializers.ValidationError(_('Tool not found'))

            edit_field_list = ['name', 'desc', 'code', 'icon', 'input_field_list', 'init_field_list', 'init_params',
                               'is_active', 'folder_id']
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

            edit_dict['update_time'] = timezone.now()
            QuerySet(Tool).filter(id=self.data.get('id')).update(**edit_dict)

            return self.one()

        def delete(self):
            self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            if tool.template_id is None and tool.icon != '':
                QuerySet(File).filter(id=tool.icon.split('/')[-1]).delete()
            QuerySet(WorkspaceUserResourcePermission).filter(target=tool.id).delete()
            QuerySet(Tool).filter(id=self.data.get('id')).delete()

        def one(self):
            self.is_one_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).select_related('user').first()
            nick_name = tool.user.nick_name if tool and tool.user else None
            if tool.init_params:
                tool.init_params = json.loads(rsa_long_decrypt(tool.init_params))
            if tool.init_field_list:
                password_fields = [i["field"] for i in tool.init_field_list if
                                   i.get("input_type") == "PasswordInput"]
                if tool.init_params:
                    for k in tool.init_params:
                        if k in password_fields and tool.init_params[k]:
                            tool.init_params[k] = encryption(tool.init_params[k])
            return {
                **ToolModelSerializer(tool).data,
                'init_params': tool.init_params if tool.init_params else {},
                'nick_name': nick_name
            }

        def export(self):
            try:
                self.is_valid()
                id = self.data.get('id')
                tool = QuerySet(Tool).filter(id=id).first()
                tool_dict = ToolExportModelSerializer(tool).data
                mk_instance = ToolInstance(tool_dict, 'v2')
                tool_pickle = pickle.dumps(mk_instance)
                response = HttpResponse(content_type='text/plain', content=tool_pickle)
                response['Content-Disposition'] = f'attachment; filename="{tool.name}.tool"'
                return response
            except Exception as e:
                return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class Pylint(serializers.Serializer):

        def run(self, instance, is_valid=True):
            if is_valid:
                self.is_valid(raise_exception=True)
                PylintInstance(data=instance).is_valid(raise_exception=True)
            code = instance.get('code')
            file_name = get_file_name()
            with open(file_name, 'w') as file:
                file.write(code)
            reporter = JSON2Reporter(output=io.StringIO())
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
        folder_id = serializers.CharField(required=False, allow_null=True, label=_("folder id"))

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
            if self.data.get('folder_id') is None:
                folder_id = self.data.get('workspace_id')
            else:
                folder_id = self.data.get('folder_id')
            tool = tool_instance.tool
            tool_id = uuid.uuid7()
            tool_model = Tool(
                id=tool_id,
                name=tool.get('name'),
                desc=tool.get('desc'),
                code=tool.get('code'),
                user_id=user_id,
                workspace_id=self.data.get('workspace_id'),
                input_field_list=tool.get('input_field_list'),
                init_field_list=tool.get('init_field_list', []),
                folder_id=folder_id,
                scope=scope,
                is_active=False
            )
            tool_model.save()

            # 自动授权给创建者
            UserResourcePermissionSerializer(data={
                'workspace_id': self.data.get('workspace_id'),
                'user_id': self.data.get('user_id'),
                'auth_target_type': AuthTargetType.TOOL.value
            }).auth_resource(str(tool_id))

            return True

    class IconOperate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_("function ID"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        image = UploadedImageField(required=True, label=_("picture"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Tool).filter(id=self.data.get('id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Tool id does not exist'))

        def edit(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('id')).first()
            if tool is None:
                raise AppApiException(500, _('Function does not exist'))
            # 删除旧的图片
            if tool.icon != '':
                QuerySet(File).filter(id=tool.icon.split('/')[-1]).delete()
            if self.data.get('image') is None:
                tool.icon = ''
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

                tool.icon = f'./oss/file/{file_id}'
            tool.save()

            return tool.icon

    class InternalTool(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        name = serializers.CharField(required=False, label=_("tool name"), allow_null=True, allow_blank=True)

        def get_internal_tools(self):
            self.is_valid(raise_exception=True)
            query_set = QuerySet(Tool)

            if self.data.get('name', '') != '':
                query_set = query_set.filter(
                    Q(name__icontains=self.data.get('name')) |
                    Q(desc__icontains=self.data.get('name'))
                )

            query_set = query_set.filter(
                Q(scope=ToolScope.INTERNAL) &
                Q(is_active=True)
            )
            return ToolModelSerializer(query_set, many=True).data

    class AddInternalTool(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        tool_id = serializers.UUIDField(required=True, label=_("tool id"))

        def add(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                AddInternalToolRequest(data=instance).is_valid(raise_exception=True)

            internal_tool = QuerySet(Tool).filter(id=self.data.get('tool_id')).first()
            if internal_tool is None:
                raise AppApiException(500, _('Tool does not exist'))

            tool_id = uuid.uuid7()
            tool = Tool(
                id=tool_id,
                name=instance.get('name', internal_tool.name),
                desc=internal_tool.desc,
                code=internal_tool.code,
                user_id=self.data.get('user_id'),
                icon=internal_tool.icon,
                workspace_id=self.data.get('workspace_id'),
                input_field_list=internal_tool.input_field_list,
                init_field_list=internal_tool.init_field_list,
                scope=ToolScope.WORKSPACE,
                tool_type=ToolType.CUSTOM,
                folder_id=instance.get('folder_id', self.data.get('workspace_id')),
                template_id=internal_tool.id,
                label=internal_tool.label,
                is_active=False
            )
            tool.save()

            # 自动授权给创建者
            UserResourcePermissionSerializer(data={
                'workspace_id': self.data.get('workspace_id'),
                'user_id': self.data.get('user_id'),
                'auth_target_type': AuthTargetType.TOOL.value
            }).auth_resource(str(tool_id))

            return ToolModelSerializer(tool).data

    class StoreTool(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        name = serializers.CharField(required=False, label=_("tool name"), allow_null=True, allow_blank=True)

        def get_appstore_tools(self):
            self.is_valid(raise_exception=True)
            # 下载zip文件
            try:
                res = requests.get('https://apps-assets.fit2cloud.com/stable/maxkb.json.zip', timeout=5)
                res.raise_for_status()
                # 创建临时文件保存zip
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                    temp_zip.write(res.content)
                    temp_zip_path = temp_zip.name

                try:
                    # 解压zip文件
                    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                        # 获取zip中的第一个文件（假设只有一个json文件）
                        json_filename = zip_ref.namelist()[0]
                        json_content = zip_ref.read(json_filename)

                    # 将json转换为字典
                    tool_store = json.loads(json_content.decode('utf-8'))
                    tag_dict = {tag['name']: tag['key'] for tag in tool_store['additionalProperties']['tags']}
                    filter_apps = []
                    for tool in tool_store['apps']:
                        if self.data.get('name', '') != '':
                            if self.data.get('name').lower() not in tool.get('name', '').lower():
                                continue
                        versions = tool.get('versions', [])
                        tool['label'] = tag_dict[tool.get('tags')[0]] if tool.get('tags') else ''
                        tool['version'] = next(
                            (version.get('name') for version in versions if
                             version.get('downloadUrl') == tool['downloadUrl']),
                        )
                        filter_apps.append(tool)

                    tool_store['apps'] = filter_apps
                    return tool_store
                finally:
                    # 清理临时文件
                    os.unlink(temp_zip_path)
            except Exception as e:
                maxkb_logger.error(f"fetch appstore tools error: {e}")
                return {'apps': [], 'additionalProperties': {'tags': []}}

    class AddStoreTool(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        tool_id = serializers.CharField(required=True, label=_("tool id"))

        def add(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                AddInternalToolRequest(data=instance).is_valid(raise_exception=True)

            versions = instance.get('versions', [])
            download_url = instance.get('download_url')
            # 查找匹配的版本名称
            version_name = next(
                (version.get('name') for version in versions if version.get('downloadUrl') == download_url),
            )
            res = requests.get(download_url, timeout=5)
            tool_data = RestrictedUnpickler(io.BytesIO(res.content)).load().tool
            tool_id = uuid.uuid7()
            tool = Tool(
                id=tool_id,
                name=instance.get('name'),
                desc=tool_data.get('desc'),
                code=tool_data.get('code'),
                user_id=self.data.get('user_id'),
                icon=instance.get('icon', ''),
                workspace_id=self.data.get('workspace_id'),
                input_field_list=tool_data.get('input_field_list', []),
                init_field_list=tool_data.get('init_field_list', []),
                scope=ToolScope.WORKSPACE,
                tool_type=ToolType.CUSTOM,
                folder_id=instance.get('folder_id', self.data.get('workspace_id')),
                template_id=self.data.get('tool_id'),
                label=instance.get('label'),
                version=version_name,
                is_active=False
            )
            tool.save()

            # 自动授权给创建者
            UserResourcePermissionSerializer(data={
                'workspace_id': self.data.get('workspace_id'),
                'user_id': self.data.get('user_id'),
                'auth_target_type': AuthTargetType.TOOL.value
            }).auth_resource(str(tool_id))
            try:
                requests.get(instance.get('download_callback_url'), timeout=5)
            except Exception as e:
                maxkb_logger.error(f"callback appstore tool download error: {e}")
            return ToolModelSerializer(tool).data

    class UpdateStoreTool(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        tool_id = serializers.UUIDField(required=True, label=_("tool id"))
        download_url = serializers.CharField(required=True, label=_("download url"))
        download_callback_url = serializers.CharField(required=True, label=_("download callback url"))
        icon = serializers.CharField(required=True, label=_("icon"), allow_null=True, allow_blank=True)
        versions = serializers.ListField(required=True, label=_("versions"), child=serializers.DictField())

        def update_tool(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get('tool_id')).first()
            if tool is None:
                raise AppApiException(500, _('Tool does not exist'))
            # 查找匹配的版本名称
            version_name = next(
                (version.get('name') for version in self.data.get('versions') if
                 version.get('downloadUrl') == self.data.get('download_url')),
            )
            res = requests.get(self.data.get('download_url'), timeout=5)
            tool_data = RestrictedUnpickler(io.BytesIO(res.content)).load().tool
            tool.desc = tool_data.get('desc')
            tool.code = tool_data.get('code')
            tool.input_field_list = tool_data.get('input_field_list', [])
            tool.init_field_list = tool_data.get('init_field_list', [])
            tool.icon = self.data.get('icon', tool.icon)
            tool.version = version_name
            # tool.is_active = False
            tool.save()
            try:
                requests.get(self.data.get('download_callback_url'), timeout=5)
            except Exception as e:
                maxkb_logger.error(f"callback appstore tool download error: {e}")
            return ToolModelSerializer(tool).data


class ToolTreeSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        folder_id = serializers.CharField(required=True, label=_('folder id'))
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('tool name'))
        user_id = serializers.UUIDField(required=False, allow_null=True, label=_('user id'))
        scope = serializers.CharField(required=True, label=_('scope'))
        tool_type = serializers.CharField(required=False, label=_('tool type'), allow_null=True, allow_blank=True)
        create_user = serializers.UUIDField(required=False, label=_('create user'), allow_null=True)

        def page_tool(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)

            folder_id = self.data.get('folder_id', self.data.get('workspace_id'))
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

        def get_query_set(self, workspace_manage, is_x_pack_ee):
            tool_query_set = QuerySet(Tool).filter(workspace_id=self.data.get('workspace_id'))
            folder_query_set = QuerySet(ToolFolder)
            default_query_set = QuerySet(Tool)

            workspace_id = self.data.get('workspace_id')
            user_id = self.data.get('user_id')
            scope = self.data.get('scope')
            tool_type = self.data.get('tool_type')
            desc = self.data.get('desc')
            name = self.data.get('name')
            folder_id = self.data.get('folder_id')
            create_user = self.data.get('create_user')

            if workspace_id is not None:
                folder_query_set = folder_query_set.filter(workspace_id=workspace_id)
                default_query_set = default_query_set.filter(workspace_id=workspace_id)
            if folder_id is not None and folder_id != workspace_id:
                folder_query_set = folder_query_set.filter(parent=folder_id)
                default_query_set = default_query_set.filter(folder_id=folder_id)
            if name is not None:
                folder_query_set = folder_query_set.filter(name__icontains=name)
                default_query_set = default_query_set.filter(name__icontains=name)
            if desc is not None:
                folder_query_set = folder_query_set.filter(desc__icontains=desc)
                default_query_set = default_query_set.filter(desc__icontains=desc)
            if create_user is not None:
                tool_query_set = tool_query_set.filter(user_id=create_user)
                folder_query_set = folder_query_set.filter(user_id=create_user)

            default_query_set = default_query_set.order_by("-create_time")

            if scope is not None:
                tool_query_set = tool_query_set.filter(scope=scope)
            if tool_type:
                tool_query_set = tool_query_set.filter(tool_type=tool_type)

            query_set_dict = {
                'tool_query_set': tool_query_set,
                'default_query_set': default_query_set,
            }
            if not workspace_manage:
                query_set_dict['workspace_user_resource_permission_query_set'] = QuerySet(
                    WorkspaceUserResourcePermission).filter(
                    auth_target_type="TOOL",
                    workspace_id=workspace_id,
                    user_id=user_id
                )
            return query_set_dict

        @staticmethod
        def is_x_pack_ee():
            workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
            role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
            return workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None

        def page_tool_with_folders(self, current_page: int, page_size: int):
            self.is_valid(raise_exception=True)

            workspace_manage = is_workspace_manage(self.data.get('user_id'), self.data.get('workspace_id'))
            is_x_pack_ee = self.is_x_pack_ee()

            return native_page_search(
                current_page, page_size, self.get_query_set(workspace_manage, is_x_pack_ee),
                get_file_content(
                    os.path.join(
                        PROJECT_DIR,
                        "apps", "tools", 'sql',
                        'list_tool.sql' if workspace_manage else (
                            'list_tool_user_ee.sql' if is_x_pack_ee else 'list_tool_user.sql'
                        )
                    )
                ),
                post_records_handler=lambda record: {
                    **record,
                    'input_field_list': json.loads(record.get('input_field_list', '[]')),
                    'init_field_list': json.loads(record.get('init_field_list', '[]')),
                },
            )

        def get_tools(self):
            self.is_valid(raise_exception=True)

            workspace_manage = is_workspace_manage(self.data.get('user_id'), self.data.get('workspace_id'))
            is_x_pack_ee = self.is_x_pack_ee()
            results = native_search(
                self.get_query_set(workspace_manage, is_x_pack_ee),
                get_file_content(
                    os.path.join(
                        PROJECT_DIR,
                        "apps", "tools", 'sql',
                        'list_tool.sql' if workspace_manage else (
                            'list_tool_user_ee.sql' if is_x_pack_ee else 'list_tool_user.sql'
                        )
                    )
                ),

            )

            # 返回包含文件夹和工具的结构
            return {
                'folders': [
                    folder for folder in results if folder['resource_type'] == 'folder'
                ],
                'tools': [
                    {
                        **tool,
                        'input_field_list': json.loads(tool.get('input_field_list', '[]')),
                        'init_field_list': json.loads(tool.get('init_field_list', '[]')),
                    } for tool in results if tool['resource_type'] == 'tool'
                ],
            }
