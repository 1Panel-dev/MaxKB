# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_key.py
    @date：2023/11/7 10:50
    @desc:
"""
from drf_yasg import openapi

from common.mixins.api_mixin import ApiMixin


class ApplicationApi(ApiMixin):
    class EditApplicationIcon(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='file',
                                  in_=openapi.IN_FORM,
                                  type=openapi.TYPE_FILE,
                                  required=True,
                                  description='上传文件')
            ]

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

    class Model(ApiMixin):
        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='application_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='应用id'),
                    openapi.Parameter(name='model_type', in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='模型类型'),
                    ]

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
                        'allow_cross_domain': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否允许跨域",
                                                             description="是否允许跨域"),
                        'cross_domain_list': openapi.Schema(type=openapi.TYPE_ARRAY, title='跨域列表',
                                                            items=openapi.Schema(type=openapi.TYPE_STRING))
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
                    'access_num': openapi.Schema(type=openapi.TYPE_NUMBER, title="访问次数", description="访问次数"),
                    'white_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启白名单",
                                                   description="是否开启白名单"),
                    'white_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                 items=openapi.Schema(type=openapi.TYPE_STRING), title="白名单列表",
                                                 description="白名单列表"),
                    'show_source': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否显示知识来源",
                                                  description="是否显示知识来源"),
                }
            )

    class Edit(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="应用名称", description="应用名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="应用描述", description="应用描述"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮对话",
                                                               description="是否开启多轮对话"),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="开场白", description="开场白"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="关联知识库Id列表", description="关联知识库Id列表"),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="问题优化",
                                                           description="是否开启问题优化", default=True),
                    'icon': openapi.Schema(type=openapi.TYPE_STRING, title="icon",
                                           description="icon", default="/ui/favicon.ico"),
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api()

                }
            )

    class WorkFlow(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[''],
                properties={
                    'nodes': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                            title="节点列表", description="节点列表",
                                            default=[]),
                    'edges': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                            title='连线列表', description="连线列表",
                                            default={}),

                }
            )

    class DatasetSetting(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[''],
                properties={
                    'top_n': openapi.Schema(type=openapi.TYPE_NUMBER, title="引用分段数", description="引用分段数",
                                            default=5),
                    'similarity': openapi.Schema(type=openapi.TYPE_NUMBER, title='相似度', description="相似度",
                                                 default=0.6),
                    'max_paragraph_char_number': openapi.Schema(type=openapi.TYPE_NUMBER, title='最多引用字符数',
                                                                description="最多引用字符数", default=3000),
                    'search_mode': openapi.Schema(type=openapi.TYPE_STRING, title='检索模式',
                                                  description="embedding|keywords|blend", default='embedding'),
                    'no_references_setting': openapi.Schema(type=openapi.TYPE_OBJECT, title='检索模式',
                                                            required=['status', 'value'],
                                                            properties={
                                                                'status': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                         title="状态",
                                                                                         description="ai作答:ai_questioning,指定回答:designated_answer",
                                                                                         default='ai_questioning'),
                                                                'value': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                        title="值",
                                                                                        description="ai作答:就是题词,指定回答:就是指定回答内容",
                                                                                        default='{question}'),
                                                            }),
                }
            )

    class ModelSetting(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['prompt'],
                properties={
                    'prompt': openapi.Schema(type=openapi.TYPE_STRING, title="提示词", description="提示词",
                                             default=('已知信息：'
                                                      '\n{data}'
                                                      '\n回答要求：'
                                                      '\n- 如果你不知道答案或者没有从获取答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。'
                                                      '\n- 避免提及你是从<data></data>中获得的知识。'
                                                      '\n- 请保持答案与<data></data>中描述的一致。'
                                                      '\n- 请使用markdown 语法优化答案的格式。'
                                                      '\n- <data></data>中的图片链接、链接地址和脚本语言请完整返回。'
                                                      '\n- 请使用与问题相同的语言来回答。'
                                                      '\n问题：'
                                                      '\n{question}')),

                }
            )

    class Publish(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=[],
                properties={
                    'work_flow': ApplicationApi.WorkFlow.get_request_body_api()
                }
            )

    class Create(ApiMixin):
        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'dataset_setting', 'model_setting',
                          'problem_optimization'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="应用名称", description="应用名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="应用描述", description="应用描述"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮对话",
                                                               description="是否开启多轮对话"),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="开场白", description="开场白"),
                    'dataset_id_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                      items=openapi.Schema(type=openapi.TYPE_STRING),
                                                      title="关联知识库Id列表", description="关联知识库Id列表"),
                    'dataset_setting': ApplicationApi.DatasetSetting.get_request_body_api(),
                    'model_setting': ApplicationApi.ModelSetting.get_request_body_api(),
                    'problem_optimization': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="问题优化",
                                                           description="是否开启问题优化", default=True),
                    'type': openapi.Schema(type=openapi.TYPE_STRING, title="应用类型",
                                           description="应用类型 简易:SIMPLE|工作流:WORK_FLOW")

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
