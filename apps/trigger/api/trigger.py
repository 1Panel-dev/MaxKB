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

from common.mixins.api_mixin import APIMixin
from trigger.serializers.trigger import TriggerCreateRequest, TriggerResponse


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
            )
        ]

    @staticmethod
    def get_request():
        return TriggerCreateRequest

    @staticmethod
    def get_response():
        return TriggerResponse


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