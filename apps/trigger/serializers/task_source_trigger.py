# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： task_source_trigger.py
    @date：2026/1/22 16:18
    @desc:
"""
import os.path
import re
from typing import Dict

import uuid_utils.compat as uuid
from django.core import validators
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.db.search import page_search, get_dynamics_model, native_page_search, native_search
from common.exception.app_exception import AppApiException
from common.field.common import ObjectField
from common.utils.common import get_file_content
from knowledge.serializers.common import BatchSerializer
from maxkb.conf import PROJECT_DIR
from tools.models import Tool
from trigger.models import TriggerTypeChoices, Trigger, TriggerTaskTypeChoices, TriggerTask
from trigger.serializers.trigger import TriggerModelSerializer, TriggerSerializer, ApplicationTriggerTaskSerializer, \
    ToolTriggerTaskSerializer, TriggerTaskModelSerializer


class TaskSourceTriggerSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))

    def insert(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return TriggerSerializer().insert(instance, with_valid=True)


class TaskSourceTriggerOperateSerializer(serializers.Serializer):
    trigger_id = serializers.UUIDField(required=True, label=_('trigger id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    source_type = serializers.CharField(required=True, label=_('source type'))
    source_id = serializers.CharField(required=True, label=_('source id'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Trigger).filter(id=self.data.get('trigger_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Trigger id does not exist'))

    def one(self, with_valid=True):
        if with_valid:
            self.is_valid()
        trigger_id = self.data.get('trigger_id')
        workspace_id = self.data.get('workspace_id')
        source_id = self.data.get('source_id')
        source_type = self.data.get('source_type')

        trigger = QuerySet(Trigger).filter(workspace_id=workspace_id, id=trigger_id).first()
        trigger_task = TriggerTaskModelSerializer(TriggerTask.objects.filter(
            trigger_id=trigger_id, source_id=source_id, source_type=source_type).first()).data

        if source_type == TriggerTaskTypeChoices.APPLICATION:
            application_task = ApplicationTriggerTaskSerializer(
                Application.objects.filter(workspace_id=workspace_id, id=source_id).first()).data
            return {
                **TriggerModelSerializer(trigger).data,
                'trigger_task': trigger_task,
                'application_task': application_task,
            }
        if source_type == TriggerTaskTypeChoices.TOOL:
            tool_task = ToolTriggerTaskSerializer(
                Tool.objects.filter(workspace_id=workspace_id, id=source_id).first()).data
            return {
                **TriggerModelSerializer(trigger).data,
                'trigger_task': trigger_task,
                'application_task': tool_task,
            }

    def edit(self, instance: Dict, with_valid = True):
        if with_valid:
            self.is_valid(raise_exception=True)






class TaskSourceTriggerListSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    source_type = serializers.CharField(required=True, label=_('source type'))
    source_id = serializers.CharField(required=True, label=_('source id'))

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)

        triggers = Trigger.objects.filter(workspace_id=self.data.get("workspace_id"),
                                          triggertask__source_id=self.data.get("source_id"),
                                          triggertask__source_type=self.data.get("source_type"),
                                          is_active=True
                                          ).distinct()

        return [TriggerModelSerializer(trigger).data for trigger in triggers]
