# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class ProvideResponse(ResultSerializer):
    def get_data(self):
        return ProvideSerializer()


class ProvideSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, label=_("model name"))
    provider = serializers.CharField(required=True, label=_("provider"))
    icon = serializers.CharField(required=True, label=_("icon"))


class ProvideListSerializer(serializers.Serializer):
    key = serializers.CharField(required=True, max_length=64, label=_("model name"))
    value = serializers.CharField(required=True, label=_("value"))


class ModelListSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, label=_("model name"))
    model_type = serializers.CharField(required=True, label=_("model type"))
    desc = serializers.CharField(required=True, label=_("model name"))


class ProvideApi(APIMixin):
    class ModelList(APIMixin):
        @staticmethod
        def get_query_params_api():
            return [OpenApiParameter(
                # 参数的名称是done
                name="model_type",
                # 对参数的备注
                description="model_type",
                # 指定参数的类型
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                # 指定必须给
                required=False,
            ), OpenApiParameter(
                # 参数的名称是done
                name="provider",
                # 对参数的备注
                description="provider",
                # 指定参数的类型
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                # 指定必须给
                required=True,
            )
            ]

        @staticmethod
        def get_response():
            return serializers.ListSerializer(child=ModelListSerializer())

    @staticmethod
    def get_response():
        return ProvideResponse

    class ModelTypeList(APIMixin):
        @staticmethod
        def get_query_params_api():
            return [OpenApiParameter(
                # 参数的名称是done
                name="provider",
                # 对参数的备注
                description="provider",
                # 指定参数的类型
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                # 指定必须给
                required=True,
            )]

        @staticmethod
        def get_response():
            return serializers.ListSerializer(child=ProvideListSerializer())
