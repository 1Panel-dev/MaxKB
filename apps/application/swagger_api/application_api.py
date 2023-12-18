# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_api.py
    @date：2023/11/7 10:50
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin

"""
  name = serializers.CharField(required=True)
    desc = serializers.CharField(required=True)
    model_id = serializers.CharField(required=True)
    multiple_rounds_dialogue = serializers.BooleanField(required=True)
    prologue = serializers.CharField(required=True)
    example = serializers.ListSerializer(required=False, child=serializers.CharField(required=True))
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True))
"""


class ApplicationApi(ApiMixin):
    class Authentication(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['access_token', ],
                properties={
                    'access_token': openapi.Schema(type=openapi.TYPE_STRING, title="应用认证token",
                                                   description="应用认证token"),

                }
            )

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'user_id', 'status', 'create_time',
                      'update_time'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description="主键id"),
                'name': openapi.Schema(type=openapi.TYPE_STRING, title="应用名称", description="应用名称"),
                'desc': openapi.Schema(type=openapi.TYPE_STRING, title="应用描述", description="应用描述"),
                'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮对话",
                                                           description="是否开启多轮对话"),
                'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="开场白", description="开场白"),
                'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                          title="示例列表", description="示例列表"),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="所属用户", description="所属用户"),

                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否发布", description='是否发布'),

                'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间", description='创建时间'),

                'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间", description='修改时间'),
                'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                  items=openapi.Schema(type=openapi.TYPE_STRING),
                                                  title="关联知识库Id列表",
                                                  description="关联知识库Id列表(查询详情的时候返回)")
            }
        )

    class ApiKey(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id')

                    ]

        class Operate(ApiMixin):
            @staticmethod
            def get_request_params_api():
                return [openapi.Parameter(name='application_id',
                                          in_=openapi.IN_PATH,
                                          type=openapi.TYPE_STRING,
                                          required=True,
                                          description='应用id'),
                        openapi.Parameter(name='api_key_id',
                                          in_=openapi.IN_PATH,
                                          type=openapi.TYPE_STRING,
                                          required=True,
                                          description='应用api_key id')
                        ]

            @staticmethod
            def get_request_body_api():
                return openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=[],
                    properties={
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否激活",
                                                    description="是否激活"),

                    }
                )

    class AccessToken(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id')

                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'access_token_reset': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="重置Token",
                                                         description="重置Token"),

                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否激活", description="是否激活"),

                }
            )

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_id', 'multiple_rounds_dialogue'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="应用名称", description="应用名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="应用描述", description="应用描述"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮对话",
                                                               description="是否开启多轮对话"),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="开场白", description="开场白"),
                    'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title="示例列表", description="示例列表"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="关联知识库Id列表", description="关联知识库Id列表"),

                }
            )

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_id', 'multiple_rounds_dialogue'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="应用名称", description="应用名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="应用描述", description="应用描述"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮对话",
                                                               description="是否开启多轮对话"),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="开场白", description="开场白"),
                    'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title="示例列表", description="示例列表"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="关联知识库Id列表", description="关联知识库Id列表")

                }
            )

    class Query(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='应用名称'),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='应用描述')
                    ]

    class Operate(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id'),

                    ]
