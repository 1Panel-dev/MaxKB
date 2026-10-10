# coding=utf-8
from common.mixins.api_mixin import APIMixin
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from models_provider.serializers.prompt_generate_serializers import PromptGenerateSerializers


class PromptGenerateAPI(APIMixin):
    @staticmethod
    def get_parameters(workspace: bool = True):
        parameters = []
        if workspace:
            parameters.append(
                OpenApiParameter(
                    name="workspace_id",
                    description=_("workspace id"),
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.PATH,  # type: ignore
                    required=True,
                )
            )
        parameters.append(
            OpenApiParameter(
                name="model_id",
                description=_("model id"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            )
        )
        return parameters

    @staticmethod
    def get_request():
        return PromptGenerateSerializers
