# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： vote_api.py
    @date：2025/6/23 17:35
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from chat.serializers.chat_record import VoteRequest
from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer


class VoteAPI(APIMixin):
    @staticmethod
    def get_request():
        return VoteRequest

    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="chat_id",
            description=_("Chat ID"),
            type=OpenApiTypes.STR,
            location='path',
            required=True,
        ),
            OpenApiParameter(
                name="chat_record_id",
                description=_("Chat Record ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer
