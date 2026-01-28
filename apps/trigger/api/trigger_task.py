# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： trigger_task.py
    @date：2026/1/28 16:37
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from trigger.serializers.trigger_task import ChatRecordSerializerModel, TriggerTaskResponse


class TriggerTaskRecordResultSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True, help_text="任务记录id", label='任务记录id')
    state = serializers.CharField(required=True, help_text="任务记录状态", label='任务记录状态')
    source_type = serializers.CharField(required=True, help_text="资源类型", label='资源类型')
    source_name = serializers.CharField(required=True, help_text="资源名称", label="资源名称")
    source_id = serializers.CharField(required=True, help_text="资源id", label="资源id")
    task_record_id = serializers.CharField(required=True, help_text="资源任务记录id", label="资源任务记录id")
    trigger_id = serializers.CharField(required=True, help_text="触发器id", label="触发器id")
    type = serializers.CharField(required=True, help_text="资源类型", label="资源类型")
    create_time = serializers.CharField(required=True, help_text="创建时间", label="创建时间")
    update_time = serializers.CharField(required=True, help_text="修改时间", label="修改时间")


class TriggerTaskRecordResponse(ResultSerializer):
    def get_data(self):
        return TriggerTaskRecordResultSerializer(many=True)


class TriggerTaskRecordExecutionDetailsResponse(ResultSerializer):
    def get_data(self):
        return ChatRecordSerializerModel()


class TriggerTaskResultSerializer(ResultSerializer):
    def get_data(self):
        return TriggerTaskResponse(many=True)


class TriggerTaskAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="trigger_id",
                description="触发器id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return TriggerTaskResultSerializer


class TriggerTaskRecordPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="trigger_id",
                description="触发器id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description=_("Page size"),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description="任务名称",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="state",
                description="状态",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="order",
                description="排序字段",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return TriggerTaskRecordResponse


class TriggerTaskRecordExecutionDetailsAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="trigger_id",
                description="触发器id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="trigger_task_id",
                description="触发器任务id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return TriggerTaskRecordExecutionDetailsResponse
