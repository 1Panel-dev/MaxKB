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

    @staticmethod
    def get_request_params_api():
        pass

    @staticmethod
    def get_request_body_api():
        pass

    @staticmethod
    def get_response_body_api():
        pass
