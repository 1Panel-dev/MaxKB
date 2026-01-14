# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 11:48
    @desc:
"""

import uuid_utils.compat as uuid
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from trigger.models import TriggerTypeChoices, Trigger, TriggerTaskTypeChoices, TriggerTask


class TriggerTaskCreateRequest(serializers.Serializer):
    source_type = serializers.ChoiceField(required=True, choices=TriggerTaskTypeChoices)
    source_id = serializers.CharField(required=True, label=_('source_id'))
    is_active = serializers.BooleanField(required=False, label=_('Is active'))


class TriggerCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('trigger name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('trigger description'))
    trigger_type = serializers.ChoiceField(required=True, choices=TriggerTypeChoices)
    trigger_setting = serializers.DictField(required=True, label=_("trigger setting"))
    meta = models.JSONField(default=dict)
    is_active = serializers.BooleanField(required=False, label=_('Is active'))
    trigger_task = TriggerTaskCreateRequest(many=True)


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

        trigger_id = uuid.uuid7()

        trigger_model = Trigger(
            id=trigger_id,
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

        trigger_tasks = instance.get('trigger_task')
        if trigger_tasks:
            trigger_task_models = [
                self.to_trigger_task_model(trigger_id, task.get('source_type'), task.get('source_id')) for task in
                trigger_tasks
            ]
            TriggerTask.objects.bulk_create(trigger_task_models)
        else:
            raise AppApiException(500, _('Trigger task can not be empty'))


        return TriggerResponse(trigger_model).data

    @staticmethod
    def to_trigger_task_model(trigger_id: str, source_type: str, source_id: str):
        return TriggerTask(
            id=uuid.uuid7(),
            trigger_id=trigger_id,
            source_type=source_type,
            source_id=source_id,
            is_active=False
        )



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


class TriggerQuerySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('Trigger name'))
    type = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Trigger type'))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def get_query_set(self):
        query_set = QuerySet(Trigger).filter(workspace_id=self.data.get("workspace_id"))
        if self.data.get("name"):
            query_set = query_set.filter(name__contains=self.data.get('name'))
        if self.data.get('type'):
            query_set = query_set.filter(trigger_type=self.data.get('type'))
        return query_set

    def page(self, current_page: int, page_size: int, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return page_search(current_page, page_size, self.get_query_set(), lambda row: TriggerResponse(row).data)

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return [TriggerResponse(row).data for row in self.get_query_set()]
