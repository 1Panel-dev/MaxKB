# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 17:03
    @desc:
"""
import hashlib
import os
import re
from typing import Dict

import uuid_utils.compat as uuid
from django.core import validators
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models.application import Application, ApplicationTypeChoices, ApplicationKnowledgeMapping, \
    ApplicationFolder
from application.models.application_access_token import ApplicationAccessToken
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from knowledge.models import Knowledge
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model


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
                               folder_id=application.get('folder_id', 'root'),
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
                               folder_id=application.get('folder_id', 'root'),
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
    workspace_id = serializers.CharField(required=False, label=_('workspace id'))

    def get_query_set(self, instance: Dict):
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
        application_query_set = application_query_set.order_by("-update_time")
        return {
            'folder_query_set': folder_query_set,
            'application_query_set': application_query_set
        }

    @staticmethod
    def is_x_pack_ee():
        workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
        role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
        return workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None

    def list(self, instance: Dict):
        self.is_valid(raise_exception=True)
        ApplicationQueryRequest(data=instance).is_valid(raise_exception=True)
        return native_search(self.get_query_set(instance), select_string=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                         'list_application_ee.sql' if self.is_x_pack_ee() else 'list_application.sql')))

    def page(self, current_page: int, page_size: int, instance: Dict):
        self.is_valid(raise_exception=True)
        ApplicationQueryRequest(data=instance).is_valid(raise_exception=True)
        return native_page_search(current_page, page_size, self.get_query_set(instance), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                         'list_application_ee.sql' if self.is_x_pack_ee() else 'list_application.sql')),
                                  )


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
