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
from django.utils.translation import gettext_lazy as _


class ChatClientHistoryApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID'))
                ]

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Application ID')),
                    openapi.Parameter(name='chat_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('Conversation ID')),
                    ]

        class ReAbstract(ApiMixin):
            @staticmethod
            def get_request_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['abstract'],
                    properties={
                        'abstract': openapi.Schema(type=openapi.TYPE_STRING, title=_("abstract"),
                                                   description=_("abstract"))

                    }
                )


class OpenAIChatApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Responses(responses={
            200: openapi.Response(description=_('response parameters'),
                                  schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                        required=['id',
                                                                  'choices'],
                                                        properties={
                                                            'id': openapi.Schema(
                                                                type=openapi.TYPE_STRING,
                                                                title=_(
                                                                    "Conversation ID")),
                                                            'choices': openapi.Schema(
                                                                type=openapi.TYPE_ARRAY,
                                                                items=openapi.Schema(
                                                                    type=openapi.TYPE_OBJECT,
                                                                    required=[
                                                                        'message'],
                                                                    properties={
                                                                        'finish_reason': openapi.Schema(
                                                                            type=openapi.TYPE_STRING, ),
                                                                        'index': openapi.Schema(
                                                                            type=openapi.TYPE_INTEGER),
                                                                        'answer_list': openapi.Schema(
                                                                            type=openapi.TYPE_ARRAY,
                                                                            items=openapi.Schema(
                                                                                type=openapi.TYPE_OBJECT,
                                                                                required=[
                                                                                    'content'],
                                                                                properties={
                                                                                    'content': openapi.Schema(
                                                                                        type=openapi.TYPE_STRING),
                                                                                    'view_type': openapi.Schema(
                                                                                        type=openapi.TYPE_STRING),
                                                                                    'runtime_node_id': openapi.Schema(
                                                                                        type=openapi.TYPE_STRING),
                                                                                    'chat_record_id': openapi.Schema(
                                                                                        type=openapi.TYPE_STRING),
                                                                                    'reasoning_content': openapi.Schema(
                                                                                        type=openapi.TYPE_STRING),
                                                                                }
                                                                            )),
                                                                        'message': openapi.Schema(
                                                                            type=openapi.TYPE_OBJECT,
                                                                            required=[
                                                                                'content'],
                                                                            properties={
                                                                                'content': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING),
                                                                                'role': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING)

                                                                            }),

                                                                    }
                                                                )),
                                                            'created': openapi.Schema(
                                                                type=openapi.TYPE_INTEGER),
                                                            'model': openapi.Schema(
                                                                type=openapi.TYPE_STRING),
                                                            'object': openapi.Schema(
                                                                type=openapi.TYPE_STRING),
                                                            'usage': openapi.Schema(
                                                                type=openapi.TYPE_OBJECT,
                                                                required=[
                                                                    'completion_tokens',
                                                                    'prompt_tokens',
                                                                    'total_tokens'],
                                                                properties={
                                                                    'completion_tokens': openapi.Schema(
                                                                        type=openapi.TYPE_INTEGER),
                                                                    'prompt_tokens': openapi.Schema(
                                                                        type=openapi.TYPE_INTEGER),
                                                                    'total_tokens': openapi.Schema(
                                                                        type=openapi.TYPE_INTEGER)
                                                                })

                                                        }))})

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              required=['message'],
                              properties={
                                  'messages': openapi.Schema(type=openapi.TYPE_ARRAY, title=_("problem"),
                                                             description=_("problem"),
                                                             items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                                  required=['role', 'content'],
                                                                                  properties={
                                                                                      'content': openapi.Schema(
                                                                                          type=openapi.TYPE_STRING,
                                                                                          title=_("Question content"),
                                                                                          default=''),
                                                                                      'role': openapi.Schema(
                                                                                          type=openapi.TYPE_STRING,
                                                                                          title=_('role'),
                                                                                          default="user")
                                                                                  }
                                                                                  )),
                                  'chat_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Conversation ID")),
                                  're_chat': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("regenerate"),
                                                            default=False),
                                  'stream': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Stream Output"),
                                                           default=True)

                              })


class ChatApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title=_("problem"), description=_("problem")),
                're_chat': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("regenerate"), default=False),
                'stream': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Is it streaming output"), default=True),

                'form_data': openapi.Schema(type=openapi.TYPE_OBJECT, title=_("Form data"),
                                            description=_("Form data"),
                                            default={}),
                'image_list': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    title=_("Image list"),
                    description=_("Image list"),
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                   title=_("Image name")),
                            'url': openapi.Schema(type=openapi.TYPE_STRING,
                                                  title=_("Image URL")),
                            'file_id': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    ),
                    default=[]
                ),
                'document_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_("Document list"),
                                                description=_("Document list"),
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        # 定义对象的具体属性
                                                        'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               title=_("Document name")),
                                                        'url': openapi.Schema(type=openapi.TYPE_STRING,
                                                                              title=_("Document URL")),
                                                        'file_id': openapi.Schema(type=openapi.TYPE_STRING),
                                                    }
                                                ),
                                                default=[]),
                'audio_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_("Audio list"),
                                             description=_("Audio list"),
                                             items=openapi.Schema(
                                                 type=openapi.TYPE_OBJECT,
                                                 properties={
                                                     'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            title=_("Audio name")),
                                                     'url': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           title=_("Audio URL")),
                                                     'file_id': openapi.Schema(type=openapi.TYPE_STRING),
                                                 }
                                             ),
                                             default=[]),
                'runtime_node_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Runtime node id"),
                                                  description=_("Runtime node id"),
                                                  default=""),
                'node_data': openapi.Schema(type=openapi.TYPE_OBJECT, title=_("Node data"),
                                            description=_("Node data"),
                                            default={}),
                'chat_record_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Conversation record id"),
                                                 description=_("Conversation record id"),
                                                 default=""),
                'child_node': openapi.Schema(type=openapi.TYPE_STRING, title=_("Child node"),
                                             description=_("Child node"),
                                             default={}),

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
                'application_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application ID"),
                                                 description=_("Application ID"), default=_('Application ID')),
                'abstract': openapi.Schema(type=openapi.TYPE_STRING, title=_("abstract"),
                                           description=_("abstract"), default=_('abstract')),
                'chat_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Conversation ID"),
                                          description=_("Conversation ID"), default=_("Conversation ID")),
                'chat_record_count': openapi.Schema(type=openapi.TYPE_STRING, title=_("Number of dialogue questions"),
                                                    description=_("Number of dialogue questions"),
                                                    default=0),
                'mark_sum': openapi.Schema(type=openapi.TYPE_STRING, title=_("Number of tags"),
                                           description=_("Number of tags"), default=1),
                'star_num': openapi.Schema(type=openapi.TYPE_STRING, title=_("Number of likes"),
                                           description=_("Number of likes"), default=1),
                'trample_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_("Number of clicks"),
                                              description=_("Number of clicks"), default=1),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Change time"),
                                              description=_("Change time"),
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Creation time"),
                                              description=_("Creation time"),
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
                                      description=_('Application ID')),

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
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Application ID"),
                                         description=_(
                                             "Application ID, pass when modifying, do not pass when creating")),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Model ID"),
                                               description=_("Model ID")),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title=_("List of associated knowledge base IDs"),
                                                      description=_("List of associated knowledge base IDs")),
                    'multiple_rounds_dialogue': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                               title=_("Do you want to initiate multiple sessions"),
                                                               description=_(
                                                                   "Do you want to initiate multiple sessions")),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Problem optimization"),
                                                           description=_("Do you want to enable problem optimization"),
                                                           default=True)
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_STRING,
                title=_("Conversation ID"),
                description=_("Conversation ID"),
                default="chat_id"
            )

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID')),
                openapi.Parameter(name='history_day',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_NUMBER,
                                  required=True,
                                  description=_('Historical days')),
                openapi.Parameter(name='abstract', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description=_("abstract")),
                openapi.Parameter(name='min_star', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                  description=_("Minimum number of likes")),
                openapi.Parameter(name='min_trample', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                  description=_("Minimum number of clicks")),
                openapi.Parameter(name='comparer', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description=_("or|and comparator")),
                openapi.Parameter(name='start_time', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('start time')),
                openapi.Parameter(name='end_time', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('End time')),
                ]


class ChatRecordApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID')),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation ID')),
                openapi.Parameter(name='order_asc',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_BOOLEAN,
                                  required=False,
                                  description=_('Is it ascending order')),
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
                'chat': openapi.Schema(type=openapi.TYPE_STRING, title=_("Session log id"),
                                       description=_("Conversation log id"), default=_('Conversation log id')),
                'vote_status': openapi.Schema(type=openapi.TYPE_STRING, title=_("Voting Status"),
                                              description=_("Voting Status"), default=_("Voting Status")),
                'dataset': openapi.Schema(type=openapi.TYPE_STRING, title=_("Dataset id"), description=_("Dataset id"),
                                          default=_("Dataset id")),
                'paragraph': openapi.Schema(type=openapi.TYPE_STRING, title=_("Paragraph id"),
                                            description=_("Paragraph id"), default=1),
                'source_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Resource ID"),
                                            description=_("Resource ID"), default=1),
                'source_type': openapi.Schema(type=openapi.TYPE_STRING, title=_("Resource Type"),
                                              description=_("Resource Type"), default='xxx'),
                'message_tokens': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                 title=_("Number of tokens consumed by the question"),
                                                 description=_("Number of tokens consumed by the question"), default=0),
                'answer_tokens': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                title=_("The number of tokens consumed by the answer"),
                                                description=_("The number of tokens consumed by the answer"),
                                                default=0),
                'improve_paragraph_id_list': openapi.Schema(type=openapi.TYPE_STRING,
                                                            title=_("Improved annotation list"),
                                                            description=_("Improved annotation list"),
                                                            default=[]),
                'index': openapi.Schema(type=openapi.TYPE_STRING,
                                        title=_("Corresponding session Corresponding subscript"),
                                        description=_("Corresponding session id corresponding subscript"),
                                        default=0
                                        ),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Modification time"),
                                              description=_("Modification time"),
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Creation time"),
                                              description=_("Creation time"),
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
                                  description=_('Application ID')),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation ID')),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation record id')),
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Knowledge base id')),
                openapi.Parameter(name='document_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Document id')),
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, title=_("Section title"),
                                        description=_("Section title")),
                'content': openapi.Schema(type=openapi.TYPE_STRING, title=_("Paragraph content"),
                                          description=_("Paragraph content"))

            }
        )

    @staticmethod
    def get_request_body_api_post():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['dataset_id', 'document_id', 'chat_ids'],
            properties={
                'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Knowledge base id"),
                                             description=_("Knowledge base id")),
                'document_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Document id"),
                                              description=_("Document id")),
                'chat_ids': openapi.Schema(type=openapi.TYPE_ARRAY, title=_("Conversation id list"),
                                           description=_("Conversation id list"),
                                           items=openapi.Schema(type=openapi.TYPE_STRING))

            }
        )

    @staticmethod
    def get_request_params_api_post():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID')),
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Knowledge base id')),

                ]


class VoteApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID')),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation ID')),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation record id'))
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['vote_status'],
            properties={
                'vote_status': openapi.Schema(type=openapi.TYPE_STRING, title=_("Voting Status"),
                                              description=_("-1: Cancel vote | 0: Agree | 1: Oppose")),

            }
        )


class ChatRecordImproveApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return [openapi.Parameter(name='application_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Application ID')),
                openapi.Parameter(name='chat_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation ID')),
                openapi.Parameter(name='chat_record_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('Conversation record id'))
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
                'content': openapi.Schema(type=openapi.TYPE_STRING, title=_("Paragraph content"),
                                          description=_("Paragraph content"), default=_('Paragraph content')),
                'title': openapi.Schema(type=openapi.TYPE_STRING, title=_("title"),
                                        description=_("title"), default=_("Description of xxx")),
                'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Number of hits"),
                                          description=_("Number of hits"),
                                          default=1),
                'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Number of Likes"),
                                           description=_("Number of Likes"), default=1),
                'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_("Number of thumbs-downs"),
                                              description=_("Number of thumbs-downs"), default=1),
                'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Knowledge base id"),
                                             description=_("Knowledge base id"), default='xxx'),
                'document_id': openapi.Schema(type=openapi.TYPE_STRING, title=_("Document id"),
                                              description=_("Document id"), default='xxx'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_("Availability"),
                                            description=_("Availability"), default=True),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Modification time"),
                                              description=_("Modification time"),
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_("Creation time"),
                                              description=_("Creation time"),
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )
