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


class TaskSourceTriggerTaskEditRequest(serializers.Serializer):
    meta = serializers.DictField(default=dict, required=False)
    parameter = serializers.DictField(default=dict, required=False)


class TaskSourceTriggerEditRequest(serializers.Serializer):
    name = serializers.CharField(required=False, label=_('trigger name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('trigger description'))
    trigger_type = serializers.ChoiceField(required=False, choices=TriggerTypeChoices)
    trigger_setting = serializers.DictField(required=False, label=_("trigger setting"))
    meta = serializers.DictField(default=dict, required=False)
    trigger_task = TaskSourceTriggerTaskEditRequest(many=True, required=False)


class TaskSourceTriggerSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))

    def insert(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return TriggerSerializer().insert(instance, with_valid=True)


class TaskSourceTriggerOperateSerializer(serializers.Serializer):
    trigger_id = serializers.UUIDField(required=True, label=_('trigger id'))
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

    @transaction.atomic
    def edit(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        serializer = TaskSourceTriggerEditRequest(data=instance)
        serializer.is_valid(raise_exception=True)
        valid_data = serializer.validated_data
        trigger_id = self.data.get('trigger_id')
        workspace_id = self.data.get('workspace_id')

        trigger = Trigger.objects.filter(workspace_id=workspace_id, id=trigger_id).first()
        if not trigger:
            raise serializers.ValidationError(_('Trigger not found'))
        task_source_trigger_edit_field_list = ['name', 'desc', 'trigger_type', 'trigger_setting', 'meta']

        for field in task_source_trigger_edit_field_list:
            if field in valid_data:
                setattr(trigger, field, valid_data.get(field))
        trigger.save()

        return self.one()

    # 删除的是当前trigger_id+source_id+source_type对应的task
    @transaction.atomic
    def delete(self):
        self.is_valid(raise_exception=True)
        trigger_id = self.data.get('trigger_id')
        workspace_id = self.data.get('workspace_id')
        source_id = self.data.get('source_id')
        source_type = self.data.get('source_type')

        trigger = Trigger.objects.filter(workspace_id=workspace_id,id=trigger_id).first()
        if not trigger:
            raise AppApiException(404, _('Trigger not found'))
        delete_count = TriggerTask.objects.filter(trigger_id=trigger_id, source_id=source_id,
                                                     source_type=source_type).delete()[0]
        if delete_count == 0:
            raise AppApiException(404, _('Task not found'))
        has_other_tasks = TriggerTask.objects.filter(trigger_id=trigger_id).exists()

        if not has_other_tasks:
            trigger.delete()
        return True

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
