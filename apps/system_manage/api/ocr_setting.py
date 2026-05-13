# coding=utf-8
"""
    @project: maxkb
    @file: ocr_setting.py
    @desc: OCR 设置 API schema（drf-spectacular）。
"""
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.ocr_setting import OcrSettingSerializer


class OcrResponse(ResultSerializer):
    def get_data(self):
        return OcrSettingSerializer.Create()


class OcrSettingAPI(APIMixin):
    @staticmethod
    def get_request():
        return OcrSettingSerializer.Create()

    @staticmethod
    def get_response():
        return OcrResponse
