# coding=utf-8
"""
    @project: maxkb
    @file: display.py
    @desc: 外观/白标设置 API schema（供 drf-spectacular 生成 OpenAPI 文档使用）。
"""
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.display import DisplayInfoSerializer


class DisplayResponse(ResultSerializer):
    def get_data(self):
        return DisplayInfoSerializer.Create()


class DisplayAPI(APIMixin):
    @staticmethod
    def get_request():
        return DisplayInfoSerializer.Create()

    @staticmethod
    def get_response():
        return DisplayResponse
