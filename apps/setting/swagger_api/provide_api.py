# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： provide_api.py
    @date：2023/11/2 14:25
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _


class ModelQueryApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='name',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description=_('name')),
                openapi.Parameter(name='model_type', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description=_('model type')),
                openapi.Parameter(name='model_name', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description=_('model name')),
                openapi.Parameter(name='provider',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description=_('provider')),
                ]


class ModelEditApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('parameters required to call the function'),
                              description=_('parameters required to call the function'),
                              required=['provide', 'model_info'],
                              properties={
                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                         title=_('name'),
                                                         description=_('name')),
                                  'model_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('model type'),
                                                               description=_('model type')),
                                  'model_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('model name'),
                                                               description=_('model name')),
                                  'provider': openapi.Schema(type=openapi.TYPE_STRING,
                                                             title=_('provider'),
                                                             description=_('provider')),
                                  'credential': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               title=_('model certificate information'),
                                                               description=_('model certificate information'))
                              }
                              )


class ModelCreateApi(ApiMixin):

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('parameters required to call the function'),
                              description=_('parameters required to call the function'),
                              required=['provide', 'model_info'],
                              properties={
                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                         title=_('name'),
                                                         description=_('name')),
                                  'provider': openapi.Schema(type=openapi.TYPE_STRING,
                                                             title=_('provider'),
                                                             description=_('provider')),
                                  'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title=_('permission'),
                                                                    description="PUBLIC|PRIVATE"),
                                  'model_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('model type'),
                                                               description=_('model type')),
                                  'model_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title=_('model name'),
                                                               description=_('model name')),
                                  'credential': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               title=_('model certificate information'),
                                                               description=_('model certificate information')),

                              }
                              )


class ProvideApi(ApiMixin):
    class ModelTypeList(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('provider')),
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['key', 'value'],
                properties={
                    'key': openapi.Schema(type=openapi.TYPE_STRING, title=_('model type description'),
                                          description=_('model type description'), default=_('large language model')),
                    'value': openapi.Schema(type=openapi.TYPE_STRING, title=_('model type value'),
                                            description=_('model type value'), default="LLM"),

                }
            )

    class ModelList(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('provider')),
                    openapi.Parameter(name='model_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('model type')),
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_type'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('name'),
                                           description=_('name'), default=_('name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('model description'),
                                           description=_('model description')),
                    'model_type': openapi.Schema(type=openapi.TYPE_STRING, title=_('model type value'),
                                                 description=_('model type value'), default="LLM"),

                }
            )

    class ModelForm(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('provider')),
                    openapi.Parameter(name='model_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('model type')),
                    openapi.Parameter(name='model_name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('model name')),
                    ]

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='provider',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('provider')),
                openapi.Parameter(name='method',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description=_('function that needs to be executed')),
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title=_('parameters required to call the function'),
                              description=_('parameters required to call the function'),
                              )
