from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_access_token import ApiKeyEnableEditSerializer
from application.serializers.application_api_key import EditApplicationKeySerializer, ApplicationKeySerializerModel
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer


class ApplicationKeyListResult(ResultSerializer):
    def get_data(self):
        return ApplicationKeySerializerModel(many=True)


class ApplicationKeyResult(ResultSerializer):
    def get_data(self):
        return ApplicationKeySerializerModel()


class ApiKeyEnableResult(ResultSerializer):
    def get_data(self):
        return ApiKeyEnableEditSerializer()


class ApplicationKeyAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description="application ID",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return ApplicationKeyResult

    class List(APIMixin):
        @staticmethod
        def get_response():
            return ApplicationKeyListResult

    class Operate(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                *ApplicationKeyAPI.get_parameters(),
                OpenApiParameter(
                    name="api_key_id",
                    description="ApiKeyId",
                    type=OpenApiTypes.STR,
                    location="path",
                    required=True,
                ),
            ]

        @staticmethod
        def get_request():
            return EditApplicationKeySerializer

    class Enable(APIMixin):
        @staticmethod
        def get_parameters():
            return [
                *ApplicationKeyAPI.get_parameters(),
                OpenApiParameter(
                    name="enable_api_key",
                    description="是否启用 api key 访问应用",
                    type=OpenApiTypes.BOOL,
                    location="query",
                    required=True,
                ),
            ]

        @staticmethod
        def get_request():
            return None

        @staticmethod
        def get_response():
            return ApiKeyEnableResult
