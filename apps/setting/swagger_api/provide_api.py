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


class ModelQueryApi(ApiMixin):
    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='name',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='模型名称'),
                openapi.Parameter(name='model_type', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='模型类型'),
                openapi.Parameter(name='model_name', in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='基础模型名称'),
                openapi.Parameter(name='provider',
                                  in_=openapi.IN_QUERY,
                                  type=openapi.TYPE_STRING,
                                  required=False,
                                  description='供应名称')
                ]


class ModelEditApi(ApiMixin):
    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="调用函数所需要的参数",
                              description="调用函数所需要的参数",
                              required=['provide', 'model_info'],
                              properties={
                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                         title="模型名称",
                                                         description="模型名称"),
                                  'model_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="供应商",
                                                               description="供应商"),
                                  'model_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="供应商",
                                                               description="供应商"),
                                  'credential': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               title="模型证书信息",
                                                               description="模型证书信息")
                              }
                              )


class ModelCreateApi(ApiMixin):

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="调用函数所需要的参数",
                              description="调用函数所需要的参数",
                              required=['provide', 'model_info'],
                              properties={
                                  'name': openapi.Schema(type=openapi.TYPE_STRING,
                                                         title="模型名称",
                                                         description="模型名称"),
                                  'provider': openapi.Schema(type=openapi.TYPE_STRING,
                                                             title="供应商",
                                                             description="供应商"),
                                  'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title="权限",
                                                                    description="PUBLIC|PRIVATE"),
                                  'model_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="供应商",
                                                               description="供应商"),
                                  'model_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                               title="供应商",
                                                               description="供应商"),
                                  'credential': openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               title="模型证书信息",
                                                               description="模型证书信息"),

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
                                      description='供应名称'),
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['key', 'value'],
                properties={
                    'key': openapi.Schema(type=openapi.TYPE_STRING, title="模型类型描述",
                                          description="模型类型描述", default="大语言模型"),
                    'value': openapi.Schema(type=openapi.TYPE_STRING, title="模型类型值",
                                            description="模型类型值", default="LLM"),

                }
            )

    class ModelList(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='供应名称'),
                    openapi.Parameter(name='model_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='模型类型'),
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_type'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="模型名称",
                                           description="模型名称", default="模型名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="模型描述",
                                           description="模型描述", default="xxx模型"),
                    'model_type': openapi.Schema(type=openapi.TYPE_STRING, title="模型类型值",
                                                 description="模型类型值", default="LLM"),

                }
            )

    class ModelForm(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='provider',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='供应名称'),
                    openapi.Parameter(name='model_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='模型类型'),
                    openapi.Parameter(name='model_name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='模型名称'),
                    ]

    @staticmethod
    def get_request_params_api():
        return [openapi.Parameter(name='provider',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='供应商'),
                openapi.Parameter(name='method',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='需要执行的函数'),
                ]

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              title="调用函数所需要的参数",
                              description="调用函数所需要的参数",
                              )
