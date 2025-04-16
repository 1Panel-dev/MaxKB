# coding=utf-8

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from tools.serializers.tool import ToolModelSerializer, ToolCreateRequest


class ToolCreateResponse(ResultSerializer):
    def get_data(self):
        return ToolModelSerializer()


class ToolCreateAPI(APIMixin):
    @staticmethod
    def get_request():
        return ToolCreateRequest

    @staticmethod
    def get_response():
        return ToolCreateResponse
