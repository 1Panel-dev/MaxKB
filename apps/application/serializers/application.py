# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 17:03
    @desc:
"""
import asyncio
import datetime
import hashlib
import json
import os
import pickle
import re
from functools import reduce
from typing import Dict, List

import uuid_utils.compat as uuid
from django.core import validators
from django.db import models, transaction
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from langchain_mcp_adapters.client import MultiServerMCPClient
from rest_framework import serializers, status
from rest_framework.utils.formatting import lazy_format

from application.flow.common import Workflow
from application.models.application import Application, ApplicationTypeChoices, ApplicationKnowledgeMapping, \
    ApplicationFolder, ApplicationVersion
from application.models.application_access_token import ApplicationAccessToken
from common import result
from common.cache_data.application_access_token_cache import del_application_access_token
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.utils.common import get_file_content, restricted_loads, generate_uuid, _remove_empty_lines
from knowledge.models import Knowledge, KnowledgeScope
from knowledge.serializers.knowledge import KnowledgeSerializer, KnowledgeModelSerializer
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id
from system_manage.models import WorkspaceUserResourcePermission, AuthTargetType
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope
from tools.serializers.tool import ToolExportModelSerializer
from users.models import User
from users.serializers.user import is_workspace_manage


def get_base_node_work_flow(work_flow):
    node_list = work_flow.get('nodes')
    base_node_list = [node for node in node_list if node.get('id') == 'base-node']
    if len(base_node_list) > 0:
        return base_node_list[-1]
    return None


class MKInstance:

    def __init__(self, application: dict, function_lib_list: List[dict], version: str, tool_list: List[dict]):
        self.application = application
        self.function_lib_list = function_lib_list
        self.version = version
        self.tool_list = tool_list

    def get_tool_list(self):
        return [*(self.tool_list or []), *(self.function_lib_list or [])]


class ApplicationSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class NoReferencesChoices(models.TextChoices):
    """订单类型"""
    ai_questioning = 'ai_questioning', 'ai回答'
    designated_answer = 'designated_answer', '指定回答'


class NoReferencesSetting(serializers.Serializer):
    status = serializers.ChoiceField(required=True, choices=NoReferencesChoices.choices,
                                     label=_("No reference status"))
    value = serializers.CharField(required=True, label=_("Prompt word"))


class KnowledgeSettingSerializer(serializers.Serializer):
    top_n = serializers.FloatField(required=True, max_value=10000, min_value=1,
                                   label=_("Reference segment number"))
    similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                        label=_("Acquaintance"))
    max_paragraph_char_number = serializers.IntegerField(required=True, min_value=500, max_value=100000,
                                                         label=_("Maximum number of quoted characters"))
    search_mode = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                  message=_("The type only supports embedding|keywords|blend"), code=500)
    ], label=_("Retrieval Mode"))

    no_references_setting = NoReferencesSetting(required=True,
                                                label=_("Segment settings not referenced"))


class ModelKnowledgeAssociation(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    model_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     label=_("Model id"))
    knowledge_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True,
                                                                                               label=_(
                                                                                                   "Knowledge base id")),
                                                   label=_("Knowledge Base List"))

    def is_valid(self, *, raise_exception=True):
        super().is_valid(raise_exception=True)
        model_id = self.data.get('model_id')
        user_id = self.data.get('user_id')
        if model_id is not None and len(model_id) > 0:
            if not QuerySet(Model).filter(id=model_id).exists():
                raise AppApiException(500, f'{_("Model does not exist")}【{model_id}】')
        knowledge_id_list = list(set(self.data.get('knowledge_id_list', [])))
        exist_knowledge_id_list = [str(knowledge.id) for knowledge in
                                   QuerySet(Knowledge).filter(id__in=knowledge_id_list, user_id=user_id)]
        for knowledge_id in knowledge_id_list:
            if not exist_knowledge_id_list.__contains__(knowledge_id):
                raise AppApiException(500, f'{_("The knowledge base id does not exist")}【{knowledge_id}】')


class ModelSettingSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=102400,
                                   label=_("Prompt word"))
    system = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=102400,
                                   label=_("Role prompts"))
    no_references_prompt = serializers.CharField(required=True, max_length=102400, allow_null=True, allow_blank=True,
                                                 label=_("No citation segmentation prompt"))
    reasoning_content_enable = serializers.BooleanField(required=False,
                                                        label=_("Thinking process switch"))
    reasoning_content_start = serializers.CharField(required=False, allow_null=True, default="<think>",
                                                    allow_blank=True, max_length=256,
                                                    trim_whitespace=False,
                                                    label=_("The thinking process begins to mark"))
    reasoning_content_end = serializers.CharField(required=False, allow_null=True, allow_blank=True, default="</think>",
                                                  max_length=256,
                                                  trim_whitespace=False,
                                                  label=_("End of thinking process marker"))


class ApplicationCreateSerializer(serializers.Serializer):
    class ApplicationResponse(serializers.ModelSerializer):
        class Meta:
            model = Application
            fields = "__all__"

    class WorkflowRequest(serializers.Serializer):
        name = serializers.CharField(required=True, max_length=64, min_length=1,
                                     label=_("Application Name"))
        desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     max_length=256, min_length=1,
                                     label=_("Application Description"))
        work_flow = serializers.DictField(required=True, label=_("Workflow Objects"))
        prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=102400,
                                         label=_("Opening remarks"))
        folder_id = serializers.CharField(required=True, label=_('folder id'))

        @staticmethod
        def to_application_model(user_id: str, workspace_id: str, application: Dict):
            default_workflow = application.get('work_flow')
            for node in default_workflow.get('nodes'):
                if node.get('id') == 'base-node':
                    node.get('properties')['node_data']['desc'] = application.get('desc')
                    node.get('properties')['node_data']['name'] = application.get('name')
                    node.get('properties')['node_data']['prologue'] = application.get('prologue')
            return Application(id=uuid.uuid7(),
                               name=application.get('name'),
                               desc=application.get('desc'),
                               workspace_id=workspace_id,
                               folder_id=application.get('folder_id', application.get('workspace_id')),
                               prologue="",
                               dialogue_number=0,
                               user_id=user_id, model_id=None,
                               knowledge_setting={},
                               model_setting={},
                               problem_optimization=False,
                               type=ApplicationTypeChoices.WORK_FLOW,
                               stt_model_enable=application.get('stt_model_enable', False),
                               stt_model_id=application.get('stt_model', None),
                               tts_model_id=application.get('tts_model', None),
                               tts_model_enable=application.get('tts_model_enable', False),
                               tts_model_params_setting=application.get('tts_model_params_setting', {}),
                               tts_type=application.get('tts_type', 'BROWSER'),
                               file_upload_enable=application.get('file_upload_enable', False),
                               file_upload_setting=application.get('file_upload_setting', {}),
                               work_flow=default_workflow
                               )

    class SimplateRequest(serializers.Serializer):
        name = serializers.CharField(required=True, max_length=64, min_length=1,
                                     label=_("application name"))
        desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     max_length=256, min_length=1,
                                     label=_("application describe"))
        folder_id = serializers.CharField(required=True, label=_('folder id'))
        model_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                         label=_("Model"))
        dialogue_number = serializers.IntegerField(required=True,
                                                   min_value=0,
                                                   max_value=1024,
                                                   label=_("Historical chat records"))
        prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=40960,
                                         label=_("Opening remarks"))
        knowledge_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
                                                       allow_null=True,
                                                       label=_("Related Knowledge Base"))
        # 数据集相关设置
        knowledge_setting = KnowledgeSettingSerializer(required=True)
        # 模型相关设置
        model_setting = ModelSettingSerializer(required=True)
        # 问题补全
        problem_optimization = serializers.BooleanField(required=True,
                                                        label=_("Question completion"))
        problem_optimization_prompt = serializers.CharField(required=False, max_length=102400,
                                                            label=_("Question completion prompt"))
        # 应用类型
        type = serializers.CharField(required=True, label=_("Application Type"),
                                     validators=[
                                         validators.RegexValidator(regex=re.compile("^SIMPLE|WORK_FLOW$"),
                                                                   message=_(
                                                                       "Application type only supports SIMPLE|WORK_FLOW"),
                                                                   code=500)
                                     ]
                                     )
        model_params_setting = serializers.DictField(required=False,
                                                     label=_('Model parameters'))

        tts_model_enable = serializers.BooleanField(required=False, label=_('Voice playback enabled'))

        tts_model_id = serializers.UUIDField(required=False, allow_null=True, label=_("Voice playback model ID"))

        tts_type = serializers.CharField(required=False, label=_('Voice playback type'))

        tts_autoplay = serializers.BooleanField(required=False, label=_('Voice playback autoplay'))

        stt_model_enable = serializers.BooleanField(required=False, label=_('Voice recognition enabled'))

        stt_model_id = serializers.UUIDField(required=False, allow_null=True, label=_('Speech recognition model ID'))

        stt_autosend = serializers.BooleanField(required=False, label=_('Voice recognition automatic transmission'))

        def is_valid(self, *, user_id=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            ModelKnowledgeAssociation(data={'user_id': user_id, 'model_id': self.data.get('model_id'),
                                            'knowledge_id_list': self.data.get('knowledge_id_list')}).is_valid()

        @staticmethod
        def to_application_model(user_id: str, workspace_id: str, application: Dict):
            return Application(id=uuid.uuid7(), name=application.get('name'), desc=application.get('desc'),
                               workspace_id=workspace_id,
                               prologue=application.get('prologue'),
                               dialogue_number=application.get('dialogue_number', 0),
                               user_id=user_id, model_id=application.get('model_id'),
                               folder_id=application.get('folder_id', application.get('workspace_id')),
                               knowledge_setting=application.get('knowledge_setting'),
                               model_setting=application.get('model_setting'),
                               problem_optimization=application.get('problem_optimization'),
                               type=ApplicationTypeChoices.SIMPLE,
                               model_params_setting=application.get('model_params_setting', {}),
                               problem_optimization_prompt=application.get('problem_optimization_prompt', None),
                               stt_model_enable=application.get('stt_model_enable', False),
                               stt_model_id=application.get('stt_model', None),
                               stt_autosend=application.get('stt_autosend', False),
                               tts_model_id=application.get('tts_model', None),
                               tts_model_enable=application.get('tts_model_enable', False),
                               tts_model_params_setting=application.get('tts_model_params_setting', {}),
                               tts_type=application.get('tts_type', 'BROWSER'),
                               file_upload_enable=application.get('file_upload_enable', False),
                               file_upload_setting=application.get('file_upload_setting', {}),
                               work_flow={}
                               )


class ApplicationQueryRequest(serializers.Serializer):
    folder_id = serializers.CharField(required=False, label=_("folder id"))
    name = serializers.CharField(required=False, label=_('Application Name'))
    desc = serializers.CharField(required=False, label=_("Application Description"))
    publish_status = serializers.ChoiceField(required=False, label=_("Publish status"),
                                             choices=[('published', _("Published")),
                                                      ('unpublished', _("Unpublished"))])
    user_id = serializers.UUIDField(required=False, label=_("User ID"))


class ApplicationListResponse(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Primary key id"), help_text=_("Primary key id"))
    name = serializers.CharField(required=True, label=_("Application Name"), help_text=_("Application Name"))
    desc = serializers.CharField(required=True, label=_("Application Description"),
                                 help_text=_("Application Description"))
    is_publish = serializers.BooleanField(required=True, label=_("Model id"), help_text=_("Model id"))
    type = serializers.CharField(required=True, label=_("Application type"), help_text=_("Application type"))
    resource_type = serializers.CharField(required=True, label=_("Resource type"), help_text=_("Resource type"))
    user_id = serializers.CharField(required=True, label=_('Affiliation user'), help_text=_("Affiliation user"))
    create_time = serializers.CharField(required=True, label=_('Creation time'), help_text=_("Creation time"))
    update_time = serializers.CharField(required=True, label=_('Modification time'), help_text=_("Modification time"))


class Query(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, label=_('Workspace ID'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))

    def get_query_set(self, instance: Dict, workspace_manage: bool, is_x_pack_ee: bool):
        folder_query_set = QuerySet(ApplicationFolder)
        application_query_set = QuerySet(Application)
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get('user_id')
        desc = instance.get('desc')
        name = instance.get('name')
        publish_status = instance.get("publish_status")
        create_user = instance.get('create_user')
        if publish_status is not None:
            is_publish = True if publish_status == "published" else False
            application_query_set = application_query_set.filter(is_publish=is_publish)
        if workspace_id is not None:
            folder_query_set = folder_query_set.filter(workspace_id=workspace_id)
            application_query_set = application_query_set.filter(workspace_id=workspace_id)
        folder_id = instance.get('folder_id')
        if folder_id is not None:
            folder_query_set = folder_query_set.filter(parent=folder_id)
            application_query_set = application_query_set.filter(folder_id=folder_id)
        if name is not None:
            folder_query_set = folder_query_set.filter(name__contains=name)
            application_query_set = application_query_set.filter(name__contains=name)
        if desc is not None:
            folder_query_set = folder_query_set.filter(desc__contains=desc)
            application_query_set = application_query_set.filter(desc__contains=desc)
        if create_user is not None:
            application_query_set = application_query_set.filter(user_id=create_user)
        application_custom_sql_query_set = application_query_set
        application_query_set = application_query_set.order_by("-update_time")

        return {'folder_query_set': folder_query_set,
                'application_query_set': application_query_set,
                'workspace_user_resource_permission_query_set': QuerySet(WorkspaceUserResourcePermission).filter(
                    auth_target_type="APPLICATION",
                    workspace_id=workspace_id,
                    user_id=user_id)} if (
            not workspace_manage) else {
            'folder_query_set': folder_query_set,
            'application_query_set': application_query_set,
            'application_custom_sql': application_custom_sql_query_set
        }

    @staticmethod
    def is_x_pack_ee():
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
        return workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None

    def list(self, instance: Dict):
        self.is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get("user_id")
        ApplicationQueryRequest(data=instance).is_valid(raise_exception=True)
        workspace_manage = is_workspace_manage(user_id, workspace_id)
        is_x_pack_ee = self.is_x_pack_ee()
        return native_search(self.get_query_set(instance, workspace_manage, is_x_pack_ee),
                             select_string=get_file_content(
                                 os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                              'list_application.sql' if workspace_manage else (
                                                  'list_application_user_ee.sql' if is_x_pack_ee else 'list_application_user.sql')
                                              )))

    def page(self, current_page: int, page_size: int, instance: Dict):
        self.is_valid(raise_exception=True)
        ApplicationQueryRequest(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get("user_id")
        workspace_manage = is_workspace_manage(user_id, workspace_id)
        is_x_pack_ee = self.is_x_pack_ee()
        return native_page_search(current_page, page_size, self.get_query_set(instance, workspace_manage, is_x_pack_ee),
                                  get_file_content(
                                      os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                   'list_application.sql' if workspace_manage else (
                                                       'list_application_user_ee.sql' if is_x_pack_ee else 'list_application_user.sql'))),
                                  )


class ApplicationImportRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))
    folder_id = serializers.CharField(required=True, label=_("Folder ID"))


class ApplicationEditSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, max_length=64, min_length=1,
                                 label=_("Application Name"))
    desc = serializers.CharField(required=False, max_length=256, min_length=1, allow_null=True, allow_blank=True,
                                 label=_("Application Description"))
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                     label=_("Model"))
    dialogue_number = serializers.IntegerField(required=False,
                                               min_value=0,
                                               max_value=1024,
                                               label=_("Historical chat records"))
    prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=102400,
                                     label=_("Opening remarks"))
    knowledge_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
                                                   label=_("Related Knowledge Base")
                                                   )
    # 数据集相关设置
    knowledge_setting = KnowledgeSettingSerializer(required=False, allow_null=True,
                                                   label=_("Dataset settings"))
    # 模型相关设置
    model_setting = ModelSettingSerializer(required=False, allow_null=True,
                                           label=_("Model setup"))
    # 问题补全
    problem_optimization = serializers.BooleanField(required=False, allow_null=True,
                                                    label=_("Question completion"))
    icon = serializers.CharField(required=False, allow_null=True, label=_("Icon"))

    model_params_setting = serializers.DictField(required=False,
                                                 label=_('Model parameters'))

    tts_model_enable = serializers.BooleanField(required=False, label=_('Voice playback enabled'))

    tts_model_id = serializers.UUIDField(required=False, allow_null=True, label=_("Voice playback model ID"))

    tts_type = serializers.CharField(required=False, label=_('Voice playback type'))

    tts_autoplay = serializers.BooleanField(required=False, label=_('Voice playback autoplay'))

    stt_model_enable = serializers.BooleanField(required=False, label=_('Voice recognition enabled'))

    stt_model_id = serializers.UUIDField(required=False, allow_null=True, label=_('Speech recognition model ID'))

    stt_autosend = serializers.BooleanField(required=False, label=_('Voice recognition automatic transmission'))


class ApplicationSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))

    def insert(self, instance: Dict):
        application_type = instance.get('type')
        if 'WORK_FLOW' == application_type:
            r = self.insert_workflow(instance)
        else:
            r = self.insert_simple(instance)
        UserResourcePermissionSerializer(data={
            'workspace_id': self.data.get('workspace_id'),
            'user_id': self.data.get('user_id'),
            'auth_target_type': AuthTargetType.APPLICATION.value
        }).auth_resource(str(r.get('id')))
        return r

    def insert_workflow(self, instance: Dict):
        self.is_valid(raise_exception=True)
        user_id = self.data.get('user_id')
        workspace_id = self.data.get('workspace_id')
        wq = ApplicationCreateSerializer.WorkflowRequest(data=instance)
        wq.is_valid(raise_exception=True)
        application_model = wq.to_application_model(user_id, workspace_id, instance)
        application_model.save()
        # 插入认证信息
        ApplicationAccessToken(application_id=application_model.id,
                               access_token=hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()[8:24]).save()
        return ApplicationCreateSerializer.ApplicationResponse(application_model).data

    @staticmethod
    def to_application_knowledge_mapping(application_id: str, knowledge_id: str):
        return ApplicationKnowledgeMapping(id=uuid.uuid7(), application_id=application_id, knowledge_id=knowledge_id)

    def insert_simple(self, instance: Dict):
        self.is_valid(raise_exception=True)
        user_id = self.data.get('user_id')
        workspace_id = self.data.get("workspace_id")
        ApplicationCreateSerializer.SimplateRequest(data=instance).is_valid(user_id=user_id, raise_exception=True)
        application_model = ApplicationCreateSerializer.SimplateRequest.to_application_model(user_id, workspace_id,
                                                                                             instance)
        knowledge_id_list = instance.get('knowledge_id_list', [])
        application_knowledge_mapping_model_list = [
            self.to_application_knowledge_mapping(application_model.id, knowledge_id) for
            knowledge_id in knowledge_id_list]
        # 插入应用
        application_model.save()
        # 插入认证信息
        ApplicationAccessToken(application_id=application_model.id,
                               access_token=hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()[8:24]).save()
        # 插入关联数据
        QuerySet(ApplicationKnowledgeMapping).bulk_create(application_knowledge_mapping_model_list)
        return ApplicationCreateSerializer.ApplicationResponse(application_model).data

    @transaction.atomic
    def import_(self, instance: dict, is_import_tool, with_valid=True):
        if with_valid:
            self.is_valid()
            ApplicationImportRequest(data=instance).is_valid(raise_exception=True)
        user_id = self.data.get('user_id')
        workspace_id = self.data.get("workspace_id")
        folder_id = instance.get('folder_id')
        mk_instance_bytes = instance.get('file').read()
        try:
            mk_instance = restricted_loads(mk_instance_bytes)
        except Exception as e:
            raise AppApiException(1001, _("Unsupported file format"))
        application = mk_instance.application
        tool_list = mk_instance.get_tool_list()
        update_tool_map = {}
        if len(tool_list) > 0:
            tool_id_list = reduce(lambda x, y: [*x, *y],
                                  [[tool.get('id'), generate_uuid((tool.get('id') + workspace_id or ''))]
                                   for tool
                                   in
                                   tool_list], [])
            # 存在的工具列表
            exits_tool_id_list = [str(tool.id) for tool in
                                  QuerySet(Tool).filter(id__in=tool_id_list, workspace_id=workspace_id)]
            # 需要更新的工具集合
            update_tool_map = {tool.get('id'): generate_uuid((tool.get('id') + workspace_id or '')) for tool
                               in
                               tool_list if
                               not exits_tool_id_list.__contains__(
                                   tool.get('id'))}

            tool_list = [{**tool, 'id': update_tool_map.get(tool.get('id'))} for tool in tool_list if
                         not exits_tool_id_list.__contains__(
                             tool.get('id')) and not exits_tool_id_list.__contains__(
                             generate_uuid((tool.get('id') + workspace_id or '')))]
        application_model = self.to_application(application, workspace_id, user_id, update_tool_map, folder_id)
        tool_model_list = [self.to_tool(f, workspace_id, user_id) for f in tool_list]
        application_model.save()
        # 插入授权数据
        UserResourcePermissionSerializer(data={
            'workspace_id': self.data.get('workspace_id'),
            'user_id': self.data.get('user_id'),
            'auth_target_type': AuthTargetType.APPLICATION.value
        }).auth_resource(str(application_model.id))
        # 插入认证信息
        ApplicationAccessToken(application_id=application_model.id,
                               access_token=hashlib.md5(str(uuid.uuid7()).encode()).hexdigest()[8:24]).save()
        if is_import_tool:
            if len(tool_model_list) > 0:
                QuerySet(Tool).bulk_create(tool_model_list)
                UserResourcePermissionSerializer(data={
                    'workspace_id': self.data.get('workspace_id'),
                    'user_id': self.data.get('user_id'),
                    'auth_target_type': AuthTargetType.TOOL.value
                }).auth_resource_batch([t.id for t in tool_model_list])
        return True

    @staticmethod
    def to_tool(tool, workspace_id, user_id):
        """
        @param workspace_id:
        @param user_id: 用户id
        @param tool: 工具
        @return:
        """

        return Tool(id=tool.get('id'),
                    user_id=user_id,
                    name=tool.get('name'),
                    code=tool.get('code'),
                    template_id=tool.get('template_id'),
                    input_field_list=tool.get('input_field_list'),
                    init_field_list=tool.get('init_field_list'),
                    is_active=False if len((tool.get('init_field_list') or [])) > 0 else tool.get('is_active'),
                    scope=ToolScope.WORKSPACE,
                    folder_id=workspace_id,
                    workspace_id=workspace_id)

    @staticmethod
    def to_application(application, workspace_id, user_id, update_tool_map, folder_id):
        work_flow = application.get('work_flow')
        for node in work_flow.get('nodes', []):
            if node.get('type') == 'tool-lib-node':
                tool_lib_id = (node.get('properties', {}).get('node_data', {}).get('tool_lib_id') or '')
                node.get('properties', {}).get('node_data', {})['tool_lib_id'] = update_tool_map.get(tool_lib_id,
                                                                                                     tool_lib_id)
            if node.get('type') == 'search-knowledge-node':
                node.get('properties', {}).get('node_data', {})['knowledge_id_list'] = []
        return Application(id=uuid.uuid7(),
                           user_id=user_id,
                           name=application.get('name'),
                           workspace_id=workspace_id,
                           folder_id=folder_id,
                           desc=application.get('desc'),
                           prologue=application.get('prologue'), dialogue_number=application.get('dialogue_number'),
                           knowledge_setting=application.get('knowledge_setting'),
                           model_setting=application.get('model_setting'),
                           model_params_setting=application.get('model_params_setting'),
                           tts_model_params_setting=application.get('tts_model_params_setting'),
                           problem_optimization=application.get('problem_optimization'),
                           icon="./favicon.ico",
                           work_flow=work_flow,
                           type=application.get('type'),
                           problem_optimization_prompt=application.get('problem_optimization_prompt'),
                           tts_model_enable=application.get('tts_model_enable'),
                           stt_model_enable=application.get('stt_model_enable'),
                           tts_type=application.get('tts_type'),
                           clean_time=application.get('clean_time'),
                           file_upload_enable=application.get('file_upload_enable'),
                           file_upload_setting=application.get('file_upload_setting'),
                           )


class TextToSpeechRequest(serializers.Serializer):
    text = serializers.CharField(required=True, label=_('Text'))


class SpeechToTextRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))


class PlayDemoTextRequest(serializers.Serializer):
    tts_model_id = serializers.UUIDField(required=True, label=_('Text to speech model ID'))


async def get_mcp_tools(servers):
    client = MultiServerMCPClient(servers)
    return await client.get_tools()


class McpServersSerializer(serializers.Serializer):
    mcp_servers = serializers.JSONField(required=True)


class ApplicationOperateSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Application).filter(id=self.data.get('application_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Application id does not exist'))

    def get_mcp_servers(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            McpServersSerializer(data=instance).is_valid(raise_exception=True)
        servers = json.loads(instance.get('mcp_servers'))
        for server, config in servers.items():
            if config.get('transport') not in ['sse', 'streamable_http']:
                raise AppApiException(500, _('Only support transport=sse or transport=streamable_http'))
        tools = []
        for server in servers:
            tools += [
                {
                    'server': server,
                    'name': tool.name,
                    'description': tool.description,
                    'args_schema': tool.args_schema,
                }
                for tool in asyncio.run(get_mcp_tools({server: servers[server]}))]
        return tools

    def delete(self, with_valid=True):
        if with_valid:
            self.is_valid()
        QuerySet(ApplicationVersion).filter(application_id=self.data.get('application_id')).delete()
        QuerySet(ApplicationKnowledgeMapping).filter(application_id=self.data.get('application_id')).delete()
        QuerySet(Application).filter(id=self.data.get('application_id')).delete()
        return True

    def export(self, with_valid=True):
        try:
            if with_valid:
                self.is_valid()
            application_id = self.data.get('application_id')
            application = QuerySet(Application).filter(id=application_id).first()
            tool_id_list = [node.get('properties', {}).get('node_data', {}).get('tool_lib_id') for node
                            in
                            application.work_flow.get('nodes', []) if
                            node.get('type') == 'tool-lib-node']
            tool_list = []
            if len(tool_id_list) > 0:
                tool_list = QuerySet(Tool).filter(id__in=tool_id_list).exclude(scope=ToolScope.SHARED)
            application_dict = ApplicationSerializerModel(application).data

            mk_instance = MKInstance(application_dict,
                                     [],
                                     'v2',
                                     [ToolExportModelSerializer(tool).data for tool in
                                      tool_list])
            application_pickle = pickle.dumps(mk_instance)
            response = HttpResponse(content_type='text/plain', content=application_pickle)
            response['Content-Disposition'] = f'attachment; filename="{application.name}.mk"'
            return response
        except Exception as e:
            return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def reset_application_version(application_version, application):
        update_field_dict = {
            'application_name': 'name', 'desc': 'desc', 'prologue': 'prologue', 'dialogue_number': 'dialogue_number',
            'user_id': 'user_id', 'model_id': 'model_id', 'knowledge_setting': 'knowledge_setting',
            'model_setting': 'model_setting', 'model_params_setting': 'model_params_setting',
            'tts_model_params_setting': 'tts_model_params_setting',
            'problem_optimization': 'problem_optimization', 'icon': 'icon', 'work_flow': 'work_flow',
            'problem_optimization_prompt': 'problem_optimization_prompt', 'tts_model_id': 'tts_model_id',
            'stt_model_id': 'stt_model_id', 'tts_model_enable': 'tts_model_enable',
            'stt_model_enable': 'stt_model_enable', 'tts_type': 'tts_type',
            'tts_autoplay': 'tts_autoplay', 'stt_autosend': 'stt_autosend', 'file_upload_enable': 'file_upload_enable',
            'file_upload_setting': 'file_upload_setting',
            'type': 'type'
        }

        for (version_field, app_field) in update_field_dict.items():
            _v = getattr(application, app_field)
            setattr(application_version, version_field, _v)

    @transaction.atomic
    def publish(self, instance, with_valid=True):
        if with_valid:
            self.is_valid()
        user_id = self.data.get('user_id')
        workspace_id = self.data.get("workspace_id")
        user = QuerySet(User).filter(id=user_id).first()
        application = QuerySet(Application).filter(id=self.data.get("application_id"),
                                                   workspace_id=workspace_id).first()
        if application.type == ApplicationTypeChoices.WORK_FLOW:
            work_flow = application.work_flow
            if work_flow is None:
                raise AppApiException(500, _("work_flow is a required field"))
            Workflow.new_instance(work_flow).is_valid()
            base_node = get_base_node_work_flow(work_flow)
            if base_node is not None:
                node_data = base_node.get('properties').get('node_data')
                if node_data is not None:
                    application.name = node_data.get('name')
                    application.desc = node_data.get('desc')
                    application.prologue = node_data.get('prologue')
            application.work_flow = work_flow
        application.publish_time = datetime.datetime.now()
        application.is_publish = True
        application.save()
        work_flow_version = ApplicationVersion(work_flow=application.work_flow, application=application,
                                               name=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                               publish_user_id=user_id,
                                               publish_user_name=user.username,
                                               workspace_id=workspace_id)
        self.reset_application_version(work_flow_version, application)
        work_flow_version.save()
        access_token = hashlib.md5(
            str(uuid.uuid7()).encode()).hexdigest()[
                       8:24]
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=application.id).first()
        if application_access_token is None:
            application_access_token = ApplicationAccessToken(application_id=application.id,
                                                              access_token=access_token, is_active=True)
            application_access_token.save()
        else:
            access_token = application_access_token.access_token
        del_application_access_token(access_token)
        return self.one(with_valid=False)

    @staticmethod
    def update_work_flow_model(instance):
        if 'nodes' not in instance.get('work_flow'):
            return
        nodes = instance.get('work_flow')['nodes']
        for node in nodes:
            if node['id'] == 'base-node':
                node_data = node['properties']['node_data']
                if 'stt_model_id' in node_data:
                    instance['stt_model_id'] = node_data['stt_model_id']
                if 'tts_model_id' in node_data:
                    instance['tts_model_id'] = node_data['tts_model_id']
                if 'stt_model_enable' in node_data:
                    instance['stt_model_enable'] = node_data['stt_model_enable']
                if 'tts_model_enable' in node_data:
                    instance['tts_model_enable'] = node_data['tts_model_enable']
                if 'tts_type' in node_data:
                    instance['tts_type'] = node_data['tts_type']
                if 'tts_autoplay' in node_data:
                    instance['tts_autoplay'] = node_data['tts_autoplay']
                if 'stt_autosend' in node_data:
                    instance['stt_autosend'] = node_data['stt_autosend']
                if 'tts_model_params_setting' in node_data:
                    instance['tts_model_params_setting'] = node_data['tts_model_params_setting']
                if 'file_upload_enable' in node_data:
                    instance['file_upload_enable'] = node_data['file_upload_enable']
                if 'file_upload_setting' in node_data:
                    instance['file_upload_setting'] = node_data['file_upload_setting']
                if 'name' in node_data:
                    instance['name'] = node_data['name']
                break

    @transaction.atomic
    def edit(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid()
            ApplicationEditSerializer(data=instance).is_valid(
                raise_exception=True)
        application_id = self.data.get("application_id")

        application = QuerySet(Application).get(id=application_id)
        if instance.get('model_id') is None or len(instance.get('model_id')) == 0:
            application.model_id = None
        else:
            model = QuerySet(Model).filter(
                id=instance.get('model_id')).first()
            if model is None:
                raise AppApiException(500, _("Model does not exist"))
        if instance.get('stt_model_id') is None or len(instance.get('stt_model_id')) == 0:
            application.stt_model_id = None
        else:
            model = QuerySet(Model).filter(
                id=instance.get('stt_model_id')).first()
            if model is None:
                raise AppApiException(500, _("Model does not exist"))
        if instance.get('tts_model_id') is None or len(instance.get('tts_model_id')) == 0:
            application.tts_model_id = None
        else:
            model = QuerySet(Model).filter(
                id=instance.get('tts_model_id')).first()
            if model is None:
                raise AppApiException(500, _("Model does not exist"))
        if 'work_flow' in instance:
            # 修改语音配置相关
            self.update_work_flow_model(instance)
        update_keys = ['name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'prologue', 'status',
                       'knowledge_setting', 'model_setting', 'problem_optimization', 'dialogue_number',
                       'stt_model_id', 'tts_model_id', 'tts_model_enable', 'stt_model_enable', 'tts_type',
                       'tts_autoplay', 'stt_autosend', 'file_upload_enable', 'file_upload_setting',
                       'api_key_is_active', 'icon', 'work_flow', 'model_params_setting', 'tts_model_params_setting',
                       'problem_optimization_prompt', 'clean_time', 'folder_id']
        for update_key in update_keys:
            if update_key in instance and instance.get(update_key) is not None:
                application.__setattr__(update_key, instance.get(update_key))
        application.save()

        if 'knowledge_id_list' in instance:
            knowledge_id_list = instance.get('knowledge_id_list')
            # 当前用户可修改关联的知识库列表
            application_knowledge_id_list = [str(knowledge.get('id')) for knowledge in
                                             self.list_knowledge(with_valid=False)]
            for knowledge_id in knowledge_id_list:
                if not application_knowledge_id_list.__contains__(knowledge_id):
                    message = lazy_format(_('Unknown knowledge base id {dataset_id}, unable to associate'),
                                          dataset_id=knowledge_id)
                    raise AppApiException(500, str(message))

            self.save_application_knowledge_mapping(application_knowledge_id_list, knowledge_id_list, application_id)
        return self.one(with_valid=False)

    def one(self, with_valid=True):
        if with_valid:
            self.is_valid()
        application_id = self.data.get("application_id")
        application = QuerySet(Application).get(id=application_id)
        available_knowledge_list = self.list_knowledge(with_valid=False)
        available_knowledge_dict = {knowledge.get('id'): knowledge for knowledge in available_knowledge_list}
        knowledge_list = []
        knowledge_id_list = []
        if application.type == 'SIMPLE':
            mapping_knowledge_list = QuerySet(ApplicationKnowledgeMapping).filter(application_id=application_id)
            knowledge_list = [available_knowledge_dict.get(str(km.knowledge_id)) for km in mapping_knowledge_list if
                              available_knowledge_dict.__contains__(str(km.knowledge_id))]
            knowledge_id_list = [k.get('id') for k in knowledge_list]
        else:
            self.update_knowledge_node(application.work_flow, available_knowledge_dict)

        return {**ApplicationSerializerModel(application).data,
                'knowledge_id_list': knowledge_id_list,
                'knowledge_list': knowledge_list}

    @staticmethod
    def get_search_node(work_flow):
        if work_flow is None:
            return []
        return [node for node in work_flow.get('nodes', []) if node.get('type', '') == 'search-knowledge-node']

    def update_knowledge_node(self, workflow, available_knowledge_dict):
        """
        修改知识库检索节点 数据
        定义 all_knowledge_id_list:    所有的关联知识库
            knowledge_id_list:          当前用户可看到的关联知识库列表
            knowledge_list:           用户
        @param workflow:              知识库
        @param available_knowledge_dict:   当前用户可用的知识库
        @return:
        """
        knowledge_node_list = self.get_search_node(workflow)
        for search_node in knowledge_node_list:
            node_data = search_node.get('properties', {}).get('node_data', {})
            # 当前知识库关联的所有知识库
            knowledge_id_list = node_data.get('knowledge_id_list', [])
            knowledge_list = [available_knowledge_dict.get(knowledge_id) for knowledge_id in knowledge_id_list if
                              available_knowledge_dict.__contains__(knowledge_id)]
            node_data['all_knowledge_id_list'] = knowledge_id_list
            node_data['knowledge_id_list'] = [knowledge.get('id') for knowledge in knowledge_list]
            node_data['knowledge_list'] = knowledge_list

    def list_knowledge(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        user_id = self.data.get('user_id')
        knowledge_workspace_authorization_model = DatabaseModelManage.get_model('knowledge_workspace_authorization')
        share_knowledge_list = []
        if knowledge_workspace_authorization_model is not None:
            white_list_condition = Q(authentication_type='WHITE_LIST') & Q(
                workspace_id_list__contains=[workspace_id])
            default_condition = ~Q(authentication_type='WHITE_LIST') & ~Q(
                workspace_id_list__contains=[workspace_id])
            # 组合查询
            query = white_list_condition | default_condition
            inner = QuerySet(knowledge_workspace_authorization_model).filter(query)
            share_knowledge_list = [{**KnowledgeModelSerializer(k).data, 'scope': 'SHARED'} for k in
                                    QuerySet(Knowledge).filter(id__in=inner)]
        workspace_knowledge_list = [{**k, 'scope': 'WORKSPACE'} for k in KnowledgeSerializer.Query(
            data={
                'workspace_id': workspace_id,
                'scope': KnowledgeScope.WORKSPACE,
                'user_id': user_id
            }
        ).list() if k.get('resource_type') == 'knowledge']

        return [*workspace_knowledge_list, *share_knowledge_list]

    @staticmethod
    def save_application_knowledge_mapping(application_knowledge_id_list, knowledge_id_list, application_id):
        # 需要排除已删除的数据集
        knowledge_id_list = [knowledge.id for knowledge in QuerySet(Knowledge).filter(id__in=knowledge_id_list)]
        # 删除已经关联的id
        QuerySet(ApplicationKnowledgeMapping).filter(knowledge_id__in=application_knowledge_id_list,
                                                     application_id=application_id).delete()
        # 插入
        QuerySet(ApplicationKnowledgeMapping).bulk_create(
            [ApplicationKnowledgeMapping(application_id=application_id, knowledge_id=knowledge_id) for knowledge_id in
             knowledge_id_list]) if len(knowledge_id_list) > 0 else None

    def speech_to_text(self, instance, debug=True, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            SpeechToTextRequest(data=instance).is_valid(raise_exception=True)
        application_id = self.data.get('application_id')
        if debug:
            application = QuerySet(Application).filter(id=application_id).first()
        else:
            application = QuerySet(ApplicationVersion).filter(application_id=application_id).order_by(
                '-create_time').first()
        if application.stt_model_enable:
            model = get_model_instance_by_model_workspace_id(application.stt_model_id, application.workspace_id)
            text = model.speech_to_text(instance.get('file'))
            return text

    def text_to_speech(self, instance, debug=True, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            TextToSpeechRequest(data=instance).is_valid(raise_exception=True)
        application_id = self.data.get('application_id')
        if debug:
            application = QuerySet(Application).filter(id=application_id).first()
        else:
            application = QuerySet(ApplicationVersion).filter(application_id=application_id).order_by(
                '-create_time').first()
        if application.tts_model_enable:
            model = get_model_instance_by_model_workspace_id(application.tts_model_id, application.workspace_id,
                                                             **application.tts_model_params_setting)
            content = _remove_empty_lines(instance.get('text', ''))

            return model.text_to_speech(content)

    def play_demo_text(self, instance, with_valid=True):
        text = '你好，这里是语音播放测试'
        if with_valid:
            self.is_valid(raise_exception=True)
            PlayDemoTextRequest(data=instance).is_valid(raise_exception=True)
        tts_model_id = instance.pop('tts_model_id')
        model = get_model_instance_by_model_workspace_id(tts_model_id, self.data.get('workspace_id'), **instance)
        return model.text_to_speech(text)
