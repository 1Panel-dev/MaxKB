# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_access_token.py
    @date：2025/6/9 17:46
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_access_token import AccessTokenEditSerializer
from common.mixins.api_mixin import APIMixin


class ApplicationAccessTokenAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="workspace_id",
            description="工作空间id",
            type=OpenApiTypes.STR,
            location='path',
            required=True,
        ), OpenApiParameter(
            name="application_id",
            description="应用id",
            type=OpenApiTypes.STR,
            location='path',
            required=True,
        )]

    @staticmethod
    def get_request():
        return AccessTokenEditSerializer
