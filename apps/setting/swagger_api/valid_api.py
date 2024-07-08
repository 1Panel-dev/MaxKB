# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： valid_api.py
    @date：2024/7/8 17:52
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ValidApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='valid_type',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='校验类型:application|dataset|user'),
                openapi.Parameter(name='valid_count',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='校验数量')
                ]
