# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py
    @date：2026/1/14 15:49
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from knowledge.serializers.common import BatchSerializer
from trigger.serializers.task_source_trigger import TaskSourceTriggerEditRequest
from trigger.serializers.trigger import TriggerCreateRequest, TriggerResponse, BatchActiveSerializer


class TriggerQueryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True, help_text="触发器id", label='触发器id')
    workspace_id = serializers.CharField(required=True, help_text="触发器工作空间", label='触发器工作空间')
    name = serializers.CharField(required=True, help_text="触发器名称", label='触发器名称')
    desc = serializers.CharField(required=True, help_text="触发器描述", label="触发器描述")
    trigger_type = serializers.CharField(required=True, help_text="触发器类型", label="触发器类型")
    type = serializers.CharField(required=True, help_text="资源类型", label="资源类型")
    is_active = serializers.BooleanField(required=True, help_text="是否激活", label="是否激活")
    source_name = serializers.CharField(required=True, help_text="资源类型", label="资源类型")
    source_icon = serializers.CharField(required=True, help_text="资源图标", label="资源图标")
    create_time = serializers.CharField(required=True, help_text="创建时间", label="创建时间")
    update_time = serializers.CharField(required=True, help_text="修改时间", label="修改时间")


class TriggerTaskRecordResponse(ResultSerializer):
    def get_data(self):
        return TriggerQueryResponseSerializer(many=True)


class TriggerQueryAPI(APIMixin):
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
                name="name",
                description="触发器名称",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="type",
                description="触发器类型",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="task",
                description="任务名称",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="is_active",
                description="启用状态",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="create_user",
                description="创建者",
                type=OpenApiTypes.STR,
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return TriggerTaskRecordResponse


class TriggerQueryPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [TriggerQueryAPI.get_parameters(),
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
                )]

    @staticmethod
    def get_response():
        return TriggerQueryAPI.get_response()


class TriggerCreateAPI(APIMixin):
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
        ]

    @staticmethod
    def get_request():
        return TriggerCreateRequest

    @staticmethod
    def get_response():
        return TriggerResponse


class TaskSourceTriggerCreateAPI(APIMixin):
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
                name="source_id",
                description="资源id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="source_type",
                description="资源类型",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return TriggerCreateRequest

    @staticmethod
    def get_response():
        return TriggerResponse


class TriggerBatchDeleteAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_request():
        return BatchSerializer


class TriggerBatchActiveAPI(APIMixin):
    @staticmethod
    def get_request():
        return BatchActiveSerializer


class TriggerOperateAPI(APIMixin):
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
    def get_request():
        return TriggerCreateRequest

    @staticmethod
    def get_response():
        return TriggerResponse


class RequestSE(serializers.Serializer):
    pass


class TriggerEditAPI(APIMixin):
    @staticmethod
    def get_request():
        return TriggerCreateRequest


class TaskSourceTriggerAPI(APIMixin):
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
                name="source_id",
                description="资源id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="source_type",
                description="资源类型",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return TriggerResponse


class TaskSourceTriggerOperateAPI(APIMixin):
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
                name="source_id",
                description="资源id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="source_type",
                description="资源类型",
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
    def get_request():
        return TaskSourceTriggerEditRequest
