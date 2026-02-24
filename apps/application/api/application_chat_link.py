"""
    @project: MaxKB
    @Author: niu
    @file: application_chat_link.py
    @date: 2026/2/9 16:59
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from django.utils.translation import gettext_lazy as _

from application.serializers.application_chat_link import ChatRecordShareLinkRequestSerializer
from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer


class ChatRecordLinkAPI(APIMixin):
    @staticmethod
    def get_response():
        return DefaultResultSerializer

    @staticmethod
    def get_request():
        return ChatRecordShareLinkRequestSerializer

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="application_id",
                description="Application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="chat_id",
                description=_("Chat ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

class ChatRecordDetailShareAPI(APIMixin):
    @staticmethod
    def get_response():
        return DefaultResultSerializer



    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="link",
                description="链接",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]