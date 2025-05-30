# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_embed_api.py
    @date：2025/5/30 15:25
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from django.utils.translation import gettext_lazy as _

from common.result import DefaultResultSerializer


class ChatEmbedAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="host",
                description=_("host"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="protocol",
                description=_("protocol"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="token",
                description=_("token"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            )
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer
