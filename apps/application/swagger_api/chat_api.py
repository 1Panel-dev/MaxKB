# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chat_api.py
    @date：2023/11/7 17:29
    @desc:
"""
from drf_yasg import openapi

from application.swagger_api.application_api import ApplicationApi
from common.mixins.api_mixin import ApiMixin


class ChatClientHistoryApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='应用id')
                ]


class ChatApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title="问题", description="问题"),
                're_chat': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="重新生成", default=False),
                'stream': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="重新生成", default=True)

            }
        )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'application', 'abstract', 'chat_record_count', 'mark_sum', 'star_num', 'trample_num',
                      'update_time', 'create_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                     description="id", default="xx"),
                'application_id': openapi.Schema(type=openapi.TYPE_STRING, title="应用id",
                                                 description="应用id", default='应用id'),
                'abstract': openapi.Schema(type=openapi.TYPE_STRING, title="摘要",
                                           description="摘要", default='摘要'),
                'chat_id': openapi.Schema(type=openapi.TYPE_STRING, title="对话id",
                                          description="对话id", default="对话id"),
                'chat_record_count': openapi.Schema(type=openapi.TYPE_STRING, title="对话提问数量",
                                                    description="对话提问数量",
                                                    default="对话提问数量"),
                'mark_sum': openapi.Schema(type=openapi.TYPE_STRING, title="标记数量",
                                           description="标记数量", default=1),
                'star_num': openapi.Schema(type=openapi.TYPE_STRING, title="点赞数量",
                                           description="点赞数量", default=1),
                'trample_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="点踩数量",
                                              description="点踩数量", default=1),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                              description="修改时间",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                              description="创建时间",
                                              default="1970-01-01 00:00:00"
                                              )
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

    class OpenWorkFlowTemp(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api()
                }
            )

    class OpenTempChat(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['model_id', 'multiple_rounds_dialogue', 'dataset_setting', 'model_setting',
                          'problem_optimization'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="应用id",
                                         description="应用id,修改的时候传,创建的时候不传"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="关联知识库Id列表", description="关联知识库Id列表"),
                    'multiple_rounds_dialogue': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮会话",
                                                               description="是否开启多轮会话"),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="问题优化",
                                                           description="是否开启问题优化", default=True)
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
                                  description="摘要"),
                openapi.Parameter(name='min_star', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                  description="最小点赞数"),
                openapi.Parameter(name='min_trample', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                  description="最小点踩数"),
                openapi.Parameter(name='comparer', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description="or|and 比较器")
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

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'chat', 'vote_status', 'dataset', 'paragraph', 'source_id', 'source_type',
                      'message_tokens', 'answer_tokens',
                      'problem_text', 'answer_text', 'improve_paragraph_id_list'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                     description="id", default="xx"),
                'chat': openapi.Schema(type=openapi.TYPE_STRING, title="会话日志id",
                                       description="会话日志id", default='会话日志id'),
                'vote_status': openapi.Schema(type=openapi.TYPE_STRING, title="投票状态",
                                              description="投票状态", default="投票状态"),
                'dataset': openapi.Schema(type=openapi.TYPE_STRING, title="数据集id", description="数据集id",
                                          default="数据集id"),
                'paragraph': openapi.Schema(type=openapi.TYPE_STRING, title="段落id",
                                            description="段落id", default=1),
                'source_id': openapi.Schema(type=openapi.TYPE_STRING, title="资源id",
                                            description="资源id", default=1),
                'source_type': openapi.Schema(type=openapi.TYPE_STRING, title="资源类型",
                                              description="资源类型", default='xxx'),
                'message_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, title="问题消耗token数量",
                                                 description="问题消耗token数量", default=0),
                'answer_tokens': openapi.Schema(type=openapi.TYPE_INTEGER, title="答案消耗token数量",
                                                description="答案消耗token数量", default=0),
                'improve_paragraph_id_list': openapi.Schema(type=openapi.TYPE_STRING, title="改进标注列表",
                                                            description="改进标注列表",
                                                            default=[]),
                'index': openapi.Schema(type=openapi.TYPE_STRING, title="对应会话 对应下标",
                                        description="对应会话id对应下标",
                                        default="对应会话id对应下标"
                                        ),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                              description="修改时间",
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                              description="创建时间",
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )


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
                                  description='知识库id'),
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
                'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="知识库id",
                                             description="知识库id", default='xxx'),
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
