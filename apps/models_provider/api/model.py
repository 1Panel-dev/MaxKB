# coding=utf-8
from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultSerializer
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from models_provider.serializers.model_serializer import ModelCreateRequest, ModelModelSerializer
from rest_framework import serializers


class ModelCreateResponse(ResultSerializer):
    def get_data(self):
        return ModelModelSerializer()


class ModelListResponse(APIMixin):
    @staticmethod
    def get_response():
        class ModelListResult(ResultSerializer):
            def get_data(self):
                return ModelModelSerializer(many=True)

        return ModelListResult

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
                name="name",
                description=_("model name"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,  # type: ignore
                required=False,
            ),
            OpenApiParameter(
                name="model_type",
                description=_("model type"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,  # type: ignore
                required=False,
            ),
            OpenApiParameter(
                name="model_name",
                description=_("base model"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,  # type: ignore
                required=False,
            ),
            OpenApiParameter(
                name="provider",
                description=_("provider"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,  # type: ignore
                required=False,
            ),
            OpenApiParameter(
                name="create_user",
                description=_("create user"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,  # type: ignore
                required=False,
            ),
        ]


class ModelCreateAPI(APIMixin):
    @staticmethod
    def get_request():
        return ModelCreateRequest

    @staticmethod
    def get_response():
        return ModelCreateResponse

    @classmethod
    def get_parameters(cls):
        return [
            OpenApiParameter(
                name="workspace_id",
                description=_("workspace id"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            )
        ]


class GetModelApi(APIMixin):
    @staticmethod
    def get_query_params_api():
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
        return []

    @staticmethod
    def get_response():
        return ModelCreateResponse


class ModelEditApi(APIMixin):
    @staticmethod
    def get_request():
        return ModelCreateRequest

    @staticmethod
    def get_response():
        return ModelCreateResponse


class DefaultModelResponse(APIMixin):
    @staticmethod
    def get_response():
        return DefaultResultSerializer()
