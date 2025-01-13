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
from django.utils.translation import gettext_lazy as _


class DocumentApi(ApiMixin):
    class BatchEditHitHandlingApi(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title=_('id list'),
                                              description=_('id list')),
                    'hit_handling_method': openapi.Schema(type=openapi.TYPE_STRING, title=_('hit handling method'),
                                                          description="directly_return|optimization"),
                    'directly_return_similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('directly return similarity'))
                }
            )

    class Cancel(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'type': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('task type'),
                                           description=_('1|2|3 1:Vectorization|2:Generate issues|3:Synchronize documents'))
                }
            )

    class BatchCancel(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title=_('id list'),
                                              description=_('id list')),
                    'type': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('task type'),
                                           description=_('1|2|3 1:Vectorization|2:Generate issues|3:Synchronize documents'), default=1)
                }
            )

    class EmbeddingState(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'state_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_STRING),
                                                 title=_('state list'),
                                                 description=_('state list'))
                }
            )
