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


class ModelDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("model id"))
    provider = serializers.CharField(required=True, label=_("provider"))
    name = serializers.CharField(required=True, label=_("model name"))
    model_type = serializers.CharField(required=True, label=_("model type"))
    model_name = serializers.CharField(required=True, label=_("base model"))
    status = serializers.CharField(required=True, label=_("status"))
    meta = serializers.DictField(required=False, allow_null=True, label=_("model meta"))
    credential = serializers.DictField(required=False, label=_("certification information"))
    workspace_id = serializers.CharField(required=True, label=_("workspace id"))
    nick_name = serializers.CharField(required=False, allow_blank=True, label=_("nick name"))
    username = serializers.CharField(required=False, allow_blank=True, label=_("username"))


class ModelMetaSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("model id"))
    provider = serializers.CharField(required=True, label=_("provider"))
    name = serializers.CharField(required=True, label=_("model name"))
    model_type = serializers.CharField(required=True, label=_("model type"))
    model_name = serializers.CharField(required=True, label=_("base model"))
    status = serializers.CharField(required=True, label=_("status"))
    meta = serializers.DictField(required=False, allow_null=True, label=_("model meta"))
    workspace_id = serializers.CharField(required=True, label=_("workspace id"))


class ModelSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("model id"))
    provider = serializers.CharField(required=True, label=_("provider"))
    name = serializers.CharField(required=True, label=_("model name"))
    model_type = serializers.CharField(required=True, label=_("model type"))
    model_name = serializers.CharField(required=True, label=_("base model"))
    status = serializers.CharField(required=True, label=_("status"))
    meta = serializers.DictField(required=False, allow_null=True, label=_("model meta"))
    user = serializers.UUIDField(required=False, label=_("user id"))
    user_id = serializers.UUIDField(required=False, label=_("user id"))
    username = serializers.CharField(required=False, allow_blank=True, label=_("username"))
    nick_name = serializers.CharField(required=False, allow_blank=True, label=_("nick name"))
    credential = serializers.CharField(required=False, label=_("certification information"))
    model_params_form = serializers.JSONField(required=False, label=_("parameter configuration"))
    workspace_id = serializers.CharField(required=False, label=_("workspace id"))
    workspace_name = serializers.CharField(required=False, allow_blank=True, label=_("workspace name"))
    create_time = serializers.DateTimeField(required=False, label=_("create time"))
    update_time = serializers.DateTimeField(required=False, label=_("update time"))
    resource_count = serializers.IntegerField(required=False, label=_("resource count"))


class ModelGroupedListSerializer(serializers.Serializer):
    shared_model = ModelSummarySerializer(many=True)
    model = ModelSummarySerializer(many=True)


class ModelDetailResponse(ResultSerializer):
    def get_data(self):
        return ModelDetailSerializer()


class ModelMetaResponse(ResultSerializer):
    def get_data(self):
        return ModelMetaSerializer()


class ModelGroupedListResponse(APIMixin):
    @staticmethod
    def get_response():
        class ModelGroupedListResult(ResultSerializer):
            def get_data(self):
                return ModelGroupedListSerializer()

        return ModelGroupedListResult


class ModelSummaryListResponse(ResultSerializer):
    def get_data(self):
        return ModelSummarySerializer(many=True)


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
        return ModelDetailResponse


class ModelEditApi(APIMixin):
    @staticmethod
    def get_request():
        return ModelCreateRequest

    @staticmethod
    def get_response():
        return ModelDetailResponse


class DefaultModelResponse(APIMixin):
    @staticmethod
    def get_response():
        return DefaultResultSerializer
