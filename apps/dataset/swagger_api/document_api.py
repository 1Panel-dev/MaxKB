# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： document_api.py
    @date：2024/4/28 13:56
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class DocumentApi(ApiMixin):
    class BatchEditHitHandlingApi(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title="主键id列表",
                                              description="主键id列表"),
                    'hit_handling_method': openapi.Schema(type=openapi.TYPE_STRING, title="命中处理方式",
                                                          description="directly_return|optimization"),
                    'directly_return_similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title="直接返回相似度")
                }
            )
