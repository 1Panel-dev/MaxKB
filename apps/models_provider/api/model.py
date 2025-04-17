# coding=utf-8

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from models_provider.serializers.model import ModelCreateRequest, ModelModelSerializer


class ModelCreateResponse(ResultSerializer):
    def get_data(self):
        return ModelModelSerializer()


class ModelCreateAPI(APIMixin):
    @staticmethod
    def get_request():
        return ModelCreateRequest

    @staticmethod
    def get_response():
        return ModelCreateResponse
