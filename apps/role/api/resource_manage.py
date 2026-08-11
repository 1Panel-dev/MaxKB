from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin
from common.result import ResultPageSerializer


class ApplicationResourceItemResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("主键id"))
    name = serializers.CharField(required=True, label=_("应用名称"))
    type = serializers.CharField(required=True, label=_("应用类型"))
    is_publish = serializers.BooleanField(required=True, label=_("是否发布"))
    icon = serializers.CharField(required=False, allow_null=True, label=_("应用icon"))
    nick_name = serializers.CharField(required=False, allow_null=True, label=_("创建人"))
    workspace_id = serializers.CharField(required=True, label=_("工作空间id"))
    create_time = serializers.DateTimeField(required=False, allow_null=True, label=_("创建时间"))
    update_time = serializers.DateTimeField(required=False, allow_null=True, label=_("更新时间"))


class ApplicationResourcePageResponse(ResultPageSerializer):
    def get_data(self):
        return ApplicationResourceItemResponse(many=True)


class SystemApplicationAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description=_("Page size"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description=_("应用名称"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="create_user",
                description=_("创建人ID"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="type",
                description=_("应用类型 (SIMPLE/WORK_FLOW)"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
        ]

    @staticmethod
    def get_page_response():
        return ApplicationResourcePageResponse


class ApplicationAccessTokenResponse(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_("应用id"))
    access_token = serializers.CharField(required=True, label=_("访问token"))
    is_active = serializers.BooleanField(required=True, label=_("是否开启公开访问"))
    access_num = serializers.IntegerField(required=True, label=_("访问次数"))
    white_active = serializers.BooleanField(required=True, label=_("是否开启白名单"))
    white_list = serializers.ListField(child=serializers.CharField(), label=_("白名单列表"))
    show_source = serializers.BooleanField(required=True, label=_("是否显示知识来源"))
    show_exec = serializers.BooleanField(required=True, label=_("是否显示执行详情"))
    authentication = serializers.BooleanField(required=True, label=_("是否需要认证"))
    authentication_value = serializers.JSONField(required=True, label=_("认证的值"))
    language = serializers.CharField(required=False, allow_null=True, label=_("语言"))


class SystemApplicationAccessTokenAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="application_id",
                description=_("应用id"),
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return ApplicationAccessTokenResponse


class KnowledgeResourceItemResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("主键id"))
    name = serializers.CharField(required=True, label=_("知识库名称"))
    type = serializers.IntegerField(required=True, label=_("类型"))
    nick_name = serializers.CharField(required=False, allow_null=True, label=_("创建人"))
    workspace_id = serializers.CharField(required=True, label=_("工作空间id"))
    create_time = serializers.DateTimeField(required=False, allow_null=True, label=_("创建时间"))
    update_time = serializers.DateTimeField(required=False, allow_null=True, label=_("更新时间"))


class KnowledgeResourcePageResponse(ResultPageSerializer):
    def get_data(self):
        return KnowledgeResourceItemResponse(many=True)


class SystemKnowledgeAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size", description=_("Page size"), type=OpenApiTypes.INT, location="path", required=True
            ),
            OpenApiParameter(
                name="name", description=_("知识库名称"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="create_user", description=_("创建人ID"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="type", description=_("类型 (0/1/2/4)"), type=OpenApiTypes.INT, location="query", required=False
            ),
        ]

    @staticmethod
    def get_page_response():
        return KnowledgeResourcePageResponse


class ToolResourceItemResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("主键id"))
    name = serializers.CharField(required=True, label=_("工具名称"))
    tool_type = serializers.CharField(required=True, label=_("工具类型"))
    is_active = serializers.BooleanField(required=True, label=_("是否启用"))
    template_id = serializers.CharField(required=False, allow_null=True, label=_("模版id"))
    nick_name = serializers.CharField(required=False, allow_null=True, label=_("创建人"))
    workspace_id = serializers.CharField(required=True, label=_("工作空间id"))
    create_time = serializers.DateTimeField(required=False, allow_null=True, label=_("创建时间"))
    update_time = serializers.DateTimeField(required=False, allow_null=True, label=_("更新时间"))


class ToolResourcePageResponse(ResultPageSerializer):
    def get_data(self):
        return ToolResourceItemResponse(many=True)


class SystemToolAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size", description=_("Page size"), type=OpenApiTypes.INT, location="path", required=True
            ),
            OpenApiParameter(
                name="name", description=_("工具名称"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="create_user", description=_("创建人ID"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="tool_type", description=_("工具类型"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="source",
                description=_("来源 (TOOL_STORE/CUSTOM)"),
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
        ]

    @staticmethod
    def get_page_response():
        return ToolResourcePageResponse


class ModelResourceItemResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label=_("主键id"))
    name = serializers.CharField(required=True, label=_("模型名称"))
    provider = serializers.CharField(required=True, label=_("供应商"))
    model_type = serializers.CharField(required=True, label=_("模型类型"))
    model_name = serializers.CharField(required=True, label=_("基础模型"))
    nick_name = serializers.CharField(required=False, allow_null=True, label=_("创建人"))
    workspace_id = serializers.CharField(required=True, label=_("工作空间id"))
    create_time = serializers.DateTimeField(required=False, allow_null=True, label=_("创建时间"))
    update_time = serializers.DateTimeField(required=False, allow_null=True, label=_("更新时间"))


class ModelResourcePageResponse(ResultPageSerializer):
    def get_data(self):
        return ModelResourceItemResponse(many=True)


class SystemModelAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size", description=_("Page size"), type=OpenApiTypes.INT, location="path", required=True
            ),
            OpenApiParameter(
                name="name", description=_("模型名称"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="create_user", description=_("创建人ID"), type=OpenApiTypes.STR, location="query", required=False
            ),
            OpenApiParameter(
                name="model_type", description=_("模型类型"), type=OpenApiTypes.STR, location="query", required=False
            ),
        ]

    @staticmethod
    def get_page_response():
        return ModelResourcePageResponse
