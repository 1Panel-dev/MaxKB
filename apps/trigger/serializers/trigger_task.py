# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： trigger_task.py
    @date：2026/1/14 16:34
    @desc:
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from trigger.models import TriggerTask


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
