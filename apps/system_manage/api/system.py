# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： system_setting.py
    @date：2025/6/4 16:34
    @desc:
"""
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.system import SystemProfileResponseSerializer


class SystemProfileResult(ResultSerializer):
    def get_data(self):
        return SystemProfileResponseSerializer()


class SystemProfileAPI(APIMixin):
    @staticmethod
    def get_response():
        return SystemProfileResult
