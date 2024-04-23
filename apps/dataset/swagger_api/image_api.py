# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： image_api.py
    @date：2024/4/23 11:23
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ImageApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='file',
                                  in_=openapi.IN_FORM,
                                  type=openapi.TYPE_FILE,
                                  required=True,
                                  description='上传图片文件')
                ]
