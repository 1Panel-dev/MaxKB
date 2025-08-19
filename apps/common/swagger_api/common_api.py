# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2023/12/25 16:17
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class CommonApi:
    class HitTestApi(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['query_text', 'top_number', 'similarity', 'search_mode'],
                    properties={
                        'query_text': openapi.Schema(type=openapi.TYPE_STRING, title=_('query text'),
                                                      description=_('query text')),
                        'top_number': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('top number'),
                                                      description=_('top number')),
                        'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('similarity'),
                                                      description=_('similarity')),
                        'search_mode': openapi.Schema(type=openapi.TYPE_STRING, title=_('search mode'),
                                                       description=_('search mode'))
                    }
                )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'is_active', 'dataset_id',
                          'document_id', 'title',
                          'similarity', 'comprehensive_score',
                          'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_('Paragraph content'),
                                              description=_('Paragraph content'), default=_('Paragraph content')),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title=_('title'),
                                            description=_('title'), default=_('Description of xxx')),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('Number of hits'),
                                              description=_('Number of hits'),
                                              default=1),
                    'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('Number of likes'),
                                               description=_('Number of likes'), default=1),
                    'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('Number of clicks and dislikes'),
                                                  description=_('Number of clicks and dislikes'), default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset id'),
                                                 description=_('dataset id'), default='xxx'),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('document id'),
                                                  description=_('document id'), default='xxx'),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'),
                                                description=_('Is active'), default=True),
                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('relevance score'),
                                                 description=_('relevance score'), default=True),
                    'comprehensive_score': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('Comprehensive score, used for ranking'),
                                                          description=_('Comprehensive score, used for ranking'), default=True),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('Update time'),
                                                  description=_('Update time'),
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('Create time'),
                                                  description=_('Create time'),
                                                  default="1970-01-01 00:00:00"
                                                  ),

                }
            )
