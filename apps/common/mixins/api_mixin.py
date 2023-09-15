# coding=utf-8
"""
    @project: smart-doc
    @Author：虎
    @file： api_mixin.py
    @date：2023/9/14 17:50
    @desc:
"""
from rest_framework import serializers


class ApiMixin(serializers.Serializer):

    def get_request_params_api(self):
        pass

    def get_request_body_api(self):
        pass

    def get_response_body_api(self):
        pass
