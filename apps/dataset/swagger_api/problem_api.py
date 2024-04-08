# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： problem_api.py
    @date：2024/3/11 10:49
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ProblemApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'content', 'hit_num', 'dataset_id', 'create_time', 'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                     description="id", default="xx"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, title="问题内容",
                                          description="问题内容", default='问题内容'),
                'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="命中数量", description="命中数量",
                                          default=1),
                'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="知识库id",
                                             description="知识库id", default='xxx'),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                              description="修改时间",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                              description="创建时间",
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )

    class BatchOperate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                title="问题id列表",
                description="问题id列表",
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING)
            )

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    openapi.Parameter(name='problem_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='问题id')]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['content'],
                properties={
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="问题内容",
                                              description="问题内容"),

                }
            )

    class Paragraph(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return ProblemApi.Operate.get_request_params_api()

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['content'],
                properties={
                    'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=4096, title="分段内容",
                                              description="分段内容"),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, max_length=256, title="分段标题",
                                            description="分段标题"),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用", description="是否可用"),
                    'hit_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="命中次数", description="命中次数"),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                                  description="修改时间",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                                  description="创建时间",
                                                  default="1970-01-01 00:00:00"
                                                  ),
                }
            )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    openapi.Parameter(name='content',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='问题')]

    class BatchCreate(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY,
                                  items=ProblemApi.Create.get_request_body_api())

        @staticmethod
        def get_request_params_api():
            return ProblemApi.Create.get_request_params_api()

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_STRING, description="问题文本")

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id')]
