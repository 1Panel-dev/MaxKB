# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from models_provider.serializers.model_serializer import ModelModelSerializer, ModelCreateRequest
from django.utils.translation import gettext_lazy as _


class ModelCreateResponse(ResultSerializer):
    def get_data(self):
        return ModelModelSerializer()


class ModelListResponse(APIMixin):
    @staticmethod
    def get_response():
        return serializers.ListSerializer(child=ModelModelSerializer())


class ModelCreateAPI(APIMixin):
    @staticmethod
    def get_request():
        return ModelCreateRequest

    @staticmethod
    def get_response():
        return ModelCreateResponse

    @classmethod
    def get_query_params_api(cls):
        return [OpenApiParameter(
            name="workspace_id",
            description=_("workspace id"),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]


class GetModelApi(APIMixin):

    @staticmethod
    def get_query_params_api():
        return [OpenApiParameter(
            name="workspace_id",
            description=_("workspace id"),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        ), OpenApiParameter(
            name="model_id",
            description=_("model id"),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )
        ]

    @staticmethod
    def get_response():
        return ModelModelSerializer


class ModelEditApi(APIMixin):
    @staticmethod
    def get_request():
        return ModelCreateRequest

    @staticmethod
    def get_response():
        return ModelModelSerializer
