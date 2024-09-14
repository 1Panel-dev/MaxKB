# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib_api.py
    @date：2024/8/2 17:11
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class FunctionLibApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'desc', 'code', 'input_field_list', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description="主键id"),
                'name': openapi.Schema(type=openapi.TYPE_STRING, title="函数名称", description="函数名称"),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, title="函数描述", description="函数描述"),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title="函数内容", description="函数内容"),
                'input_field_list': openapi.Schema(type=openapi.TYPE_STRING, title="输入字段", description="输入字段"),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间", description="创建时间"),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间", description="修改时间"),
            }
        )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='函数名称'),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='函数描述')
                    ]

    class Debug(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'debug_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description="输入变量列表",
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=[],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="变量名",
                                                                                    description="变量名"),
                                                                                'value': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="变量值",
                                                                                    description="变量值"),
                                                                            })),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title="函数内容", description="函数内容"),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description="输入变量列表",
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=['name', 'is_required', 'source'],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="变量名",
                                                                                    description="变量名"),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title="是否必填",
                                                                                    description="是否必填"),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="字段类型",
                                                                                    description="字段类型 string|int|dict|array|float"
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="来源",
                                                                                    description="来源只支持custom|reference"),

                                                                            }))
                }
            )

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="函数名称", description="函数名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="函数描述", description="函数描述"),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title="函数内容", description="函数内容"),
                    'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title="权限", description="权限"),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用", description="是否可用"),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description="输入变量列表",
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=[],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="变量名",
                                                                                    description="变量名"),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title="是否必填",
                                                                                    description="是否必填"),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="字段类型",
                                                                                    description="字段类型 string|int|dict|array|float"
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="来源",
                                                                                    description="来源只支持custom|reference"),

                                                                            }))
                }
            )

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'code', 'input_field_list', 'permission_type'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="函数名称", description="函数名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="函数描述", description="函数描述"),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title="函数内容", description="函数内容"),
                    'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title="权限", description="权限"),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用", description="是否可用"),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description="输入变量列表",
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=['name', 'is_required', 'source'],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="变量名",
                                                                                    description="变量名"),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title="是否必填",
                                                                                    description="是否必填"),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="字段类型",
                                                                                    description="字段类型 string|int|dict|array|float"
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title="来源",
                                                                                    description="来源只支持custom|reference"),

                                                                            }))
                }
            )
