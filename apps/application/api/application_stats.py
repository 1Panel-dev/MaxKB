# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： application_stats.py
@date：2025/6/9 20:45
@desc:
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from application.serializers.application_stats import ApplicationStatsSerializer
from common.mixins.api_mixin import APIMixin
from common.result import ResultPageSerializer, ResultSerializer


class ApplicationStatsResult(ResultSerializer):
    def get_data(self):
        return ApplicationStatsSerializer(many=True)


class ApplicationRankingRecord(serializers.Serializer):
    chat_user_id = serializers.CharField()
    chat_user_type = serializers.CharField()
    asker = serializers.DictField(allow_null=True)
    total_tokens = serializers.IntegerField()
    chat_record_count = serializers.IntegerField()


class ApplicationRankingPageResult(ResultPageSerializer):
    def get_data(self):
        return ApplicationRankingRecord(many=True)


class ApplicationStatsAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description="application ID",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="start_time",
                description="start Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="end_time",
                description="end Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return ApplicationStatsResult
