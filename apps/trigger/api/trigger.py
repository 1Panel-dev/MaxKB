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

from common.mixins.api_mixin import APIMixin
from knowledge.serializers.common import BatchSerializer
from trigger.serializers.task_source_trigger import TaskSourceTriggerEditRequest
from trigger.serializers.trigger import TriggerCreateRequest, TriggerResponse, BatchActiveSerializer


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
