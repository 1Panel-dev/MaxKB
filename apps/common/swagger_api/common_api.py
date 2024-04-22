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


class CommonApi:
    class HitTestApi(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [
                    openapi.Parameter(name='query_text',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='问题文本'),
                    openapi.Parameter(name='top_number',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_NUMBER,
                                      default=10,
                                      required=True,
                                      description='topN'),
                    openapi.Parameter(name='similarity',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_NUMBER,
                                      default=0.6,
                                      required=True,
                                      description='相关性'),
                    openapi.Parameter(name='search_mode',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      default="embedding",
                                      required=True,
                                      description='检索模式embedding|keywords|blend'
                                      )
                    ]

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
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="段落内容",
                                              description="段落内容", default='段落内容'),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title="标题",
                                            description="标题", default="xxx的描述"),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="命中数量", description="命中数量",
                                              default=1),
                    'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="点赞数量",
                                               description="点赞数量", default=1),
                    'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="点踩数量",
                                                  description="点踩数", default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="知识库id",
                                                 description="知识库id", default='xxx'),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title="文档id",
                                                  description="文档id", default='xxx'),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用",
                                                description="是否可用", default=True),
                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title="相关性得分",
                                                 description="相关性得分", default=True),
                    'comprehensive_score': openapi.Schema(type=openapi.TYPE_NUMBER, title="综合得分,用于排序",
                                                          description="综合得分,用于排序", default=True),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                                  description="修改时间",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                                  description="创建时间",
                                                  default="1970-01-01 00:00:00"
                                                  ),

                }
            )
