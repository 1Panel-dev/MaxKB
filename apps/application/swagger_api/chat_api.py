# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_api.py
    @date：2023/11/7 17:29
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ChatApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title="问题", description="问题"),

            }
        )

    class OpenChat(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id'),

                    ]

    class OpenTempChat(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['model_id', 'multiple_rounds_dialogue'],
                properties={
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="关联数据集Id列表", description="关联数据集Id列表"),
                    'multiple_rounds_dialogue': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮会话",
                                                               description="是否开启多轮会话")
                }
            )

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id'),
                openapi.Parameter(name='history_day',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_NUMBER,
                                  required=True,
                                  description='历史天数'),
                openapi.Parameter(name='abstract', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description="摘要")
                ]


class ChatRecordApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='对话id'),
                ]


class ImproveApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='会话id'),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='会话记录id'),
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='数据集id'),
                openapi.Parameter(name='document_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='文档id'),
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, title="段落标题",
                                        description="段落标题"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, title="段落内容",
                                          description="段落内容")

            }
        )


class VoteApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='会话id'),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='会话记录id')
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['vote_status'],
            properties={
                'vote_status': openapi.Schema(type=openapi.TYPE_STRING, title="投票状态",
                                              description="-1:取消投票|0:赞同|1:反对"),

            }
        )


class ChatRecordImproveApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id'),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='会话id'),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='会话记录id')
                ]

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'is_active', 'dataset_id',
                      'document_id', 'title',
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
                'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="数据集id",
                                             description="数据集id", default='xxx'),
                'document_id': openapi.Schema(type=openapi.TYPE_STRING, title="文档id",
                                              description="文档id", default='xxx'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用",
                                            description="是否可用", default=True),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                              description="修改时间",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                              description="创建时间",
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )
