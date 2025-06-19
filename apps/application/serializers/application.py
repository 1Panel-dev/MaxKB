# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 17:03
    @desc:
"""
import datetime
import hashlib
import os
import pickle
import re
from typing import Dict, List

import uuid_utils.compat as uuid
from django.core import validators
from django.db import models, transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.utils.formatting import lazy_format

from application.flow.common import Workflow
from application.models.application import Application, ApplicationTypeChoices, ApplicationKnowledgeMapping, \
    ApplicationFolder, WorkFlowVersion
from application.models.application_access_token import ApplicationAccessToken
from common import result
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.utils.common import get_file_content, valid_license, restricted_loads
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model
from tools.models import Tool, ToolScope
from tools.serializers.tool import ToolModelSerializer
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
        prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=102400,
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
        def to_application_model(user_id: str, application: Dict):
            return Application(id=uuid.uuid1(), name=application.get('name'), desc=application.get('desc'),
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

    def get_query_set(self, instance: Dict, workspace_manage: bool):
        folder_query_set = QuerySet(ApplicationFolder)
        application_query_set = QuerySet(Application)
        workspace_id = self.data.get('workspace_id')
        user_id = instance.get('user_id')
        desc = instance.get('desc')
        name = instance.get('name')
        if workspace_id is not None:
            folder_query_set = folder_query_set.filter(workspace_id=workspace_id)
            application_query_set = application_query_set.filter(workspace_id=workspace_id)
        if user_id is not None:
            folder_query_set = folder_query_set.filter(user_id=user_id)
            application_query_set = application_query_set.filter(user_id=user_id)
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
        application_custom_sql_query_set = application_query_set
        application_query_set = application_query_set.order_by("-update_time")
        return {
            'folder_query_set': folder_query_set,
            'application_query_set': application_query_set,
            'application_custom_sql': application_custom_sql_query_set
        } if workspace_manage else {'folder_query_set': folder_query_set,
                                    'application_query_set': application_query_set}

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

        return native_search(self.get_query_set(instance, workspace_manage), select_string=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                         'list_application.sql' if workspace_manage else (
                             'list_application_user_ee.sql' if self.is_x_pack_ee() else 'list_application_user.sql')
                         )))

    def page(self, current_page: int, page_size: int, instance: Dict):
        self.is_valid(raise_exception=True)
        ApplicationQueryRequest(data=instance).is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        user_id = self.data.get("user_id")
        workspace_manage = is_workspace_manage(user_id, workspace_id)
        return native_page_search(current_page, page_size, self.get_query_set(instance, workspace_manage),
                                  get_file_content(
                                      os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                   'list_application.sql' if workspace_manage else (
                                                       'list_application_user_ee.sql' if self.is_x_pack_ee() else 'list_application_user.sql'))),
                                  )


class ApplicationImportRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))


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
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
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
            return self.insert_workflow(instance)
        else:
            return self.insert_simple(instance)

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
                               access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]).save()
        return ApplicationCreateSerializer.ApplicationResponse(application_model).data

    @staticmethod
    def to_application_knowledge_mapping(application_id: str, dataset_id: str):
        return ApplicationKnowledgeMapping(id=uuid.uuid1(), application_id=application_id, dataset_id=dataset_id)

    def insert_simple(self, instance: Dict):
        self.is_valid(raise_exception=True)
        user_id = self.data.get('user_id')
        ApplicationCreateSerializer.SimplateRequest(data=instance).is_valid(user_id=user_id, raise_exception=True)
        application_model = ApplicationCreateSerializer.SimplateRequest.to_application_model(user_id, instance)
        dataset_id_list = instance.get('knowledge_id_list', [])
        application_knowledge_mapping_model_list = [
            self.to_application_knowledge_mapping(application_model.id, dataset_id) for
            dataset_id in dataset_id_list]
        # 插入应用
        application_model.save()
        # 插入认证信息
        ApplicationAccessToken(application_id=application_model.id,
                               access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]).save()
        # 插入关联数据
        QuerySet(ApplicationKnowledgeMapping).bulk_create(application_knowledge_mapping_model_list)
        return ApplicationCreateSerializer.ApplicationResponse(application_model).data

    @valid_license(model=Application, count=5,
                   message=_(
                       'The community version supports up to 5 applications. If you need more applications, please contact us (https://fit2cloud.com/).'))
    @transaction.atomic
    def import_(self, instance: dict, with_valid=True):
        if with_valid:
            self.is_valid()
            ApplicationImportRequest(data=instance).is_valid(raise_exception=True)
        user_id = self.data.get('user_id')
        workspace_id = self.data.get("workspace_id")
        mk_instance_bytes = instance.get('file').read()
        try:
            mk_instance = restricted_loads(mk_instance_bytes)
        except Exception as e:
            raise AppApiException(1001, _("Unsupported file format"))
        application = mk_instance.application

        tool_list = mk_instance.get_tool_list()
        if len(tool_list) > 0:
            tool_id_list = [tool.get('id') for tool in tool_list]
            exits_tool_id_list = [str(tool.id) for tool in
                                  QuerySet(Tool).filter(id__in=tool_id_list)]
            # 获取到需要插入的函数
            tool_list = [tool for tool in tool_id_list if
                         not exits_tool_id_list.__contains__(tool.get('id'))]
        application_model = self.to_application(application, workspace_id, user_id)
        tool_model_list = [self.to_tool(f, workspace_id, user_id) for f in tool_list]
        application_model.save()
        # 插入认证信息
        ApplicationAccessToken(application_id=application_model.id,
                               access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]).save()
        QuerySet(Tool).bulk_create(tool_model_list) if len(tool_model_list) > 0 else None
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
                    input_field_list=tool.get('input_field_list'),
                    is_active=tool.get('is_active'),
                    scope=ToolScope.WORKSPACE,
                    workspace_id=workspace_id)

    @staticmethod
    def to_application(application, workspace_id, user_id):
        work_flow = application.get('work_flow')
        for node in work_flow.get('nodes', []):
            if node.get('type') == 'search-dataset-node':
                node.get('properties', {}).get('node_data', {})['dataset_id_list'] = []
        return Application(id=uuid.uuid1(),
                           user_id=user_id,
                           name=application.get('name'),
                           workspace_id=workspace_id,
                           desc=application.get('desc'),
                           prologue=application.get('prologue'), dialogue_number=application.get('dialogue_number'),
                           dataset_setting=application.get('dataset_setting'),
                           model_setting=application.get('model_setting'),
                           model_params_setting=application.get('model_params_setting'),
                           tts_model_params_setting=application.get('tts_model_params_setting'),
                           problem_optimization=application.get('problem_optimization'),
                           icon="/ui/favicon.ico",
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


class ApplicationOperateSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if not QuerySet(Application).filter(id=self.data.get('application_id')).exists():
            raise AppApiException(500, _('Application id does not exist'))

    def delete(self, with_valid=True):
        if with_valid:
            self.is_valid()
        QuerySet(Application).filter(id=self.data.get('application_id')).delete()
        return True

    def export(self, with_valid=True):
        try:
            if with_valid:
                self.is_valid()
            application_id = self.data.get('application_id')
            application = QuerySet(Application).filter(id=application_id).first()
            tool_id_list = [node.get('properties', {}).get('node_data', {}).get('tool_id') for node
                            in
                            application.work_flow.get('nodes', []) if
                            node.get('type') == 'tool-node']
            tool_list = []
            if len(tool_id_list) > 0:
                tool_list = QuerySet(Tool).filter(id__in=tool_id_list)
            application_dict = ApplicationSerializerModel(application).data

            mk_instance = MKInstance(application_dict,
                                     [],
                                     'v2',
                                     [ToolModelSerializer(tool).data for tool in
                                      tool_list])
            application_pickle = pickle.dumps(mk_instance)
            response = HttpResponse(content_type='text/plain', content=application_pickle)
            response['Content-Disposition'] = f'attachment; filename="{application.name}.mk"'
            return response
        except Exception as e:
            return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def publish(self, instance, with_valid=True):
        if with_valid:
            self.is_valid()
        user_id = self.data.get('user_id')
        workspace_id = self.data.get("workspace_id")
        user = QuerySet(User).filter(id=user_id).first()
        application = QuerySet(Application).filter(id=self.data.get("application_id"),
                                                   workspace_id=workspace_id).first()
        work_flow = instance.get('work_flow')
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
        application.save()
        work_flow_version = WorkFlowVersion(work_flow=work_flow, application=application,
                                            name=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            publish_user_id=user_id,
                                            publish_user_name=user.username,
                                            workspace_id=workspace_id)
        work_flow_version.save()
        return True

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
                       'dataset_setting', 'model_setting', 'problem_optimization', 'dialogue_number',
                       'stt_model_id', 'tts_model_id', 'tts_model_enable', 'stt_model_enable', 'tts_type',
                       'tts_autoplay', 'stt_autosend', 'file_upload_enable', 'file_upload_setting',
                       'api_key_is_active', 'icon', 'work_flow', 'model_params_setting', 'tts_model_params_setting',
                       'problem_optimization_prompt', 'clean_time']
        for update_key in update_keys:
            if update_key in instance and instance.get(update_key) is not None:
                application.__setattr__(update_key, instance.get(update_key))
        application.save()

        if 'knowledge_id_list' in instance:
            knowledge_id_list = instance.get('knowledge_id_list')
            # 当前用户可修改关联的知识库列表
            application_knowledge_id_list = [str(knowledge.id) for knowledge in
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
        knowledge_list = self.list_knowledge(with_valid=False)
        mapping_knowledge_id_list = [akm.knowledge_id for akm in
                                     QuerySet(ApplicationKnowledgeMapping).filter(application_id=application_id)]
        knowledge_id_list = [d.id for d in
                             list(filter(lambda row: mapping_knowledge_id_list.__contains__(row.id),
                                         knowledge_list))]
        return {**ApplicationSerializerModel(application).data,
                'knowledge_id_list': knowledge_id_list}

    def list_knowledge(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        knowledge_list = QuerySet(Knowledge).filter(workspace_id=workspace_id)
        return knowledge_list

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
