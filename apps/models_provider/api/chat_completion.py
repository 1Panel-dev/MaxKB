# coding=utf-8
from common.mixins.api_mixin import APIMixin
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from models_provider.serializers.chat_completion_serializers import ChatCompletionSerializers


class ChatCompletionAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description=_("workspace id"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            ),
            OpenApiParameter(
                name="model_id",
                description=_("model id"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return ChatCompletionSerializers
