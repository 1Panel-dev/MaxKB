# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： trigger_task.py
    @date：2026/1/14 16:34
    @desc:
"""
import os

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import ChatRecord
from common.db.search import native_page_search, get_dynamics_model
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from trigger.models import TriggerTask, TaskRecord


class ChatRecordSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ['id', 'chat_id', 'vote_status', 'vote_reason', 'vote_other_content', 'problem_text', 'answer_text',
                  'message_tokens', 'answer_tokens', 'const', 'improve_paragraph_id_list', 'run_time', 'index',
                  'answer_text_list', 'details',
                  'create_time', 'update_time']


class TriggerTaskResponse(serializers.ModelSerializer):
    class Meta:
        model = TriggerTask
        fields = "__all__"


class TriggerTaskQuerySerializer(serializers.Serializer):
    trigger_id = serializers.CharField(required=True, label=_("Trigger ID"))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))

    def get_query_set(self):
        query_set = QuerySet(TriggerTask).filter(workspace_id=self.data.get("workspace_id")).filter(
            trigger_id=self.data.get("trigger_id"))
        return query_set

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return [TriggerTaskResponse(row).data for row in self.get_query_set()]


class TriggerTaskRecordOperateSerializer(serializers.Serializer):
    trigger_id = serializers.CharField(required=True, label=_("Trigger ID"))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    trigger_task_id = serializers.CharField(required=True, label=_("Trigger task ID"))
    trigger_task_record_id = serializers.CharField(required=True, label=_("Trigger task record ID"))

    def get_execution_details(self, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
        task_record = QuerySet(TaskRecord).filter(trigger_id=self.data.get("trigger_id"),
                                                  trigger_task_id=self.data.get("trigger_task_id"),
                                                  id=self.data.get('trigger_task_record_id')).first()
        if not task_record:
            raise AppApiException(500, _('Trigger task record id does not exist'))
        if task_record.source_type == 'APPLICATION':
            chat_record = QuerySet(ChatRecord).filter(id=task_record.task_record_id).first()
            return ChatRecordSerializerModel(chat_record).data
        if task_record.source_type == 'TOOL':
            pass
        return None


class TriggerTaskRecordQuerySerializer(serializers.Serializer):
    trigger_id = serializers.CharField(required=True, label=_("Trigger ID"))
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Trigger task'))
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_('Trigger task'))

    def get_query_set(self):
        trigger_query_set = QuerySet(
            model=get_dynamics_model({
                'ett.state': models.CharField(),
                'sdc.name': models.CharField(),
                'ett.workspace_id': models.CharField(),
                'ett.trigger_id': models.UUIDField(),
            }))
        trigger_query_set = trigger_query_set.filter(
            **{'ett.trigger_id': self.data.get("trigger_id")})
        if self.data.get('state'):
            trigger_query_set = trigger_query_set.filter(**{'ett.state': self.data.get('state')})
        if self.data.get("name"):
            trigger_query_set = trigger_query_set.filter(**{'sdc.name__contains': self.data.get('name')})
        return trigger_query_set

    def list(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return [TriggerTaskResponse(row).data for row in self.get_query_set()]

    def page(self, current_page, page_size, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        return native_page_search(current_page, page_size, self.get_query_set(), get_file_content(
            os.path.join(PROJECT_DIR, "apps", "trigger", "sql", 'get_trigger_task_record_page_list.sql')
        ))
