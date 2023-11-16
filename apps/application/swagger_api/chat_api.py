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
                                  description='历史天数')
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
