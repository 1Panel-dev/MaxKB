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
from django.utils.translation import gettext_lazy as _


class ProblemApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'content', 'hit_num', 'dataset_id', 'create_time', 'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                     description="id", default="xx"),
                'content': openapi.Schema(type=openapi.TYPE_STRING, title=_('content'),
                                          description=_('content'), default=_('content')),
                'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('hit num'), description=_('hit num'),
                                          default=1),
                'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset id'),
                                             description=_('dataset id'), default='xxx'),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                              description=_('update time'),
                                              default="1970-01-01 00:00:00"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                              description=_('create time'),
                                              default="1970-01-01 00:00:00"
                                              )
            }
        )

    class BatchAssociation(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return ProblemApi.BatchOperate.get_request_params_api()

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['problem_id_list'],
                properties={
                    'problem_id_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_('problem id list'),
                                                      description=_('problem id list'),
                                                      items=openapi.Schema(type=openapi.TYPE_STRING)),
                    'paragraph_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_('Associated paragraph information list'),
                                                     description=_('Associated paragraph information list'),
                                                     items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                          required=['paragraph_id', 'document_id'],
                                                                          properties={
                                                                              'paragraph_id': openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  title=_('paragraph id')),
                                                                              'document_id': openapi.Schema(
                                                                                  type=openapi.TYPE_STRING,
                                                                                  title=_('document id'))
                                                                          }))

                }
            )

    class BatchOperate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('dataset id')),
                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                title=_('problem id list'),
                description=_('problem id list'),
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
                                      description=_('dataset id')),
                    openapi.Parameter(name='problem_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('problem id'))]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['content'],
                properties={
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_('content'),
                                              description=_('content')),

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
                    'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=4096, title=_('content'),
                                              description=_('content')),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, max_length=256, title=_('Section title'),
                                            description=_('Section title')),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'), description=_('Is active')),
                    'hit_num': openapi.Schema(type=openapi.TYPE_NUMBER, title=_('Hit num'), description=_('Hit num')),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                                  description=_('update time'),
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                                  description=_('create time'),
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
                                      description=_('dataset id')),
                    openapi.Parameter(name='content',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('content')),]

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
            return openapi.Schema(type=openapi.TYPE_STRING, description=_('content'), title=_('content'))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('dataset id'))]
