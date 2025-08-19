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
from django.utils.translation import gettext_lazy as _


class FunctionLibApi(ApiMixin):
    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'desc', 'code', 'input_field_list', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description=_('ID')),
                'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('function name'),
                                       description=_('function name')),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('function description'),
                                       description=_('function description')),
                'code': openapi.Schema(type=openapi.TYPE_STRING, title=_('function content'),
                                       description=_('function content')),
                'input_field_list': openapi.Schema(type=openapi.TYPE_STRING, title=_('input field'),
                                                   description=_('input field')),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                              description=_('create time')),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                              description=_('update time')),
            }
        )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('function name')),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('function description')),
                    ]

    class Debug(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'debug_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description=_('Input variable list'),
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=[],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('variable name'),
                                                                                    description=_('variable name')),
                                                                                'value': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('variable value'),
                                                                                    description=_('variable value')),
                                                                            })),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title=_('function content'),
                                           description=_('function content')),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description=_('Input variable list'),
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=['name', 'is_required', 'source'],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('variable name'),
                                                                                    description=_('variable name')),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title=_('required'),
                                                                                    description=_('required')),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('type'),
                                                                                    description=_(
                                                                                        'Field type string|int|dict|array|float')
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('source'),
                                                                                    description=_(
                                                                                        'The source only supports custom|reference')),

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
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('function name'),
                                           description=_('function name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('function description'),
                                           description=_('function description')),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title=_('function content'),
                                           description=_('function content')),
                    'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title=_('permission'),
                                                      description=_('permission')),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'),
                                                description=_('Is active')),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description=_('Input variable list'),
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=[],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('variable name'),
                                                                                    description=_('variable name')),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title=_('required'),
                                                                                    description=_('required')),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('type'),
                                                                                    description=_(
                                                                                        'Field type string|int|dict|array|float')
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('source'),
                                                                                    description=_(
                                                                                        'The source only supports custom|reference')),

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
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('function name'),
                                           description=_('function name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('function description'),
                                           description=_('function description')),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title=_('function content'),
                                           description=_('function content')),
                    'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title=_('permission'),
                                                      description=_('permission')),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'),
                                                description=_('Is active')),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description=_('Input variable list'),
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=['name', 'is_required', 'source'],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('variable name'),
                                                                                    description=_('variable name')),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title=_('required'),
                                                                                    description=_('required')),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('type'),
                                                                                    description=_(
                                                                                        'Field type string|int|dict|array|float')
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('source'),
                                                                                    description=_(
                                                                                        'The source only supports custom|reference')),

                                                                            }))
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'code', 'input_field_list', 'permission_type'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description=_('ID')),

                    'name': openapi.Schema(type=openapi.TYPE_STRING, title=_('function name'),
                                           description=_('function name')),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title=_('function description'),
                                           description=_('function description')),
                    'code': openapi.Schema(type=openapi.TYPE_STRING, title=_('function content'),
                                           description=_('function content')),
                    'permission_type': openapi.Schema(type=openapi.TYPE_STRING, title=_('permission'),
                                                      description=_('permission')),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'),
                                                description=_('Is active')),
                    'input_field_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       description=_('Input variable list'),
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                            required=['name', 'is_required', 'source'],
                                                                            properties={
                                                                                'name': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('variable name'),
                                                                                    description=_('variable name')),
                                                                                'is_required': openapi.Schema(
                                                                                    type=openapi.TYPE_BOOLEAN,
                                                                                    title=_('required'),
                                                                                    description=_('required')),
                                                                                'type': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('type'),
                                                                                    description=_(
                                                                                        'Field type string|int|dict|array|float')
                                                                                ),
                                                                                'source': openapi.Schema(
                                                                                    type=openapi.TYPE_STRING,
                                                                                    title=_('source'),
                                                                                    description=_(
                                                                                        'The source only supports custom|reference')),

                                                                            }))
                }
            )

    class Export(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('ID')),

                    ]

    class Import(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='file',
                                      in_=openapi.IN_FORM,
                                      type=openapi.TYPE_FILE,
                                      required=True,
                                      description=_('Upload image files'))
                    ]
