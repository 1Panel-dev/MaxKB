# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:48
    @desc:
"""
import asyncio
import hashlib
import json
import os
import pickle
import re
import tempfile
import zipfile
from functools import reduce
from typing import Dict, List

import requests
import uuid_utils.compat as uuid
from django.core import validators
from django.db import models, transaction
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from langchain_mcp_adapters.client import MultiServerMCPClient
from rest_framework import serializers, status
from rest_framework.utils.formatting import lazy_format

from application.flow.common import Workflow
from application.models.application import Application, ApplicationTypeChoices, \
    ApplicationFolder, ApplicationVersion, ApplicationKnowledgeMapping
from application.models.application_access_token import ApplicationAccessToken
from application.serializers.common import update_resource_mapping_by_application
from common import result
from common.cache_data.application_access_token_cache import del_application_access_token
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search, native_page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.utils.common import get_file_content, restricted_loads, generate_uuid, _remove_empty_lines, \
    bytes_to_uploaded_file
from common.utils.logger import maxkb_logger
from knowledge.models import Knowledge, KnowledgeScope
from knowledge.serializers.knowledge import KnowledgeSerializer, KnowledgeModelSerializer
from maxkb.conf import PROJECT_DIR
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id
from system_manage.models import WorkspaceUserResourcePermission, AuthTargetType
from system_manage.models.resource_mapping import ResourceMapping
from system_manage.serializers.resource_mapping_serializers import ResourceMappingSerializer
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope
from tools.serializers.tool import ToolExportModelSerializer
from trigger.models import TriggerTypeChoices, Trigger
from users.models import User
from users.serializers.user import is_workspace_manage



class TriggerTaskCreateRequest(serializers.Serializer):
    pass

class TriggerCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('trigger name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('trigger description'))
    trigger_type = serializers.ChoiceField(choices=TriggerTypeChoices)
    trigger_setting = serializers.DictField(required=True, label=_("trigger setting"))
    meta = models.JSONField(required=False, allow_null=True, allow_blank=True, default=dict)
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    trigger_task = serializers



class TriggerResponse(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = "__all__"

class TriggerSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))

    @transaction.atomic
    def insert(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            TriggerCreateRequest(data=instance).is_valid(raise_exception=True)

        trigger_model = Trigger(
            id=uuid.uuid7(),
            name=instance.get('name'),
            workspace_id=self.data.get('workspace_id'),
            desc=instance.get('desc'),
            trigger_type=instance.get('trigger_type'),
            trigger_setting=instance.get('trigger_setting'),
            meta=instance.get('meta', {}),
            is_active=False,
            user_id=self.data.get('user_id'),
        )
        trigger_model.save()



        return TriggerResponse(trigger_model).data

class TriggerOperateSerializer(serializers.Serializer):
        trigger_id = serializers.UUIDField(required=True, label=_('trigger id'))
        user_id = serializers.UUIDField(required=True, label=_("User ID"))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Trigger).filter(id=self.data.get('trigger_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Trigger id does not exist'))




