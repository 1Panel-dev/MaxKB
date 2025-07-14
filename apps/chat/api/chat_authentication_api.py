# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_authentication_api.py
    @date：2025/6/6 19:59
    @desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from chat.serializers.chat import OpenAIInstanceSerializer
from chat.serializers.chat_authentication import AnonymousAuthenticationSerializer
from common.mixins.api_mixin import APIMixin


class OpenAIAPI(APIMixin):
    @staticmethod
    def get_request():
        return OpenAIInstanceSerializer


class ChatAuthenticationAPI(APIMixin):
    @staticmethod
    def get_request():
        return AnonymousAuthenticationSerializer

    @staticmethod
    def get_parameters():
        pass

    @staticmethod
    def get_response():
        pass


class ChatAuthenticationProfileAPI(APIMixin):

    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="access_token",
            description=_("access_token"),
            type=OpenApiTypes.STR,
            location='query',
            required=True,
        )]


class ChatOpenAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return []
